import sqlite3
import sys
import uuid
from uuid import UUID
from pathlib import Path
from typing import Collection, Optional, Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor
import threading

from arkparse.logging import ArkSaveLogger
from arkparse.logging.ark_save_logger import mark_as_worker_thread
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser, GameObjectReaderConfiguration
from arkparse.parsing._fast_shim import contains_any_pattern
from arkparse.saves.header_location import HeaderLocation
from arkparse.saves.save_context import SaveContext
from arkparse.utils import TEMP_FILES_DIR


def _fast_uuid_from_bytes(b: bytes) -> UUID:
    """Create UUID from bytes, bypassing __init__ validation for speed."""
    u = object.__new__(UUID)
    object.__setattr__(u, 'int', int.from_bytes(b, 'big'))
    return u


# Detect if GIL is disabled (free-threaded Python)
def _is_parallel_enabled() -> bool:
    """Check if parallel parsing should be enabled (GIL is disabled)."""
    if hasattr(sys, '_is_gil_enabled'):
        return not sys._is_gil_enabled()
    return False


_PARALLEL_ENABLED = _is_parallel_enabled()


def _parse_single_object(obj_uuid: UUID, class_name: str, binary_data: bytes, save_context: SaveContext) -> Optional[ArkGameObject]:
    """Parse a single game object. Thread-safe for use in parallel parsing."""
    byte_buffer = ArkBinaryParser(binary_data, save_context)
    return SaveConnection.parse_as_predefined_object(obj_uuid, class_name, byte_buffer)

class SaveConnection:

    name_offset = 0
    name_count = 0
    last_name_end = 0

    nr_parsed = 0
    faulty_objects = 0
    failed_parses: Dict[str, int] = {}

    def __init__(self, save_context: SaveContext, path: Path = None, contents: bytes = None, read_only: bool = False):
        # Thread lock for database operations
        self._db_lock = threading.Lock()
        self._max_workers = 3  # Default max workers for parallel parsing

        # create temp copy of file
        temp_save_path = TEMP_FILES_DIR / (str(uuid.uuid4()) + ".ark")
        self.parsed_objects: Dict[uuid.UUID, ArkGameObject] = {}
        self._class_cache: Dict[uuid.UUID, str] = {}

        if path is not None:
            with open(path, 'rb') as file:
                with open(temp_save_path, 'wb') as temp_file:
                    temp_file.write(file.read())
        elif contents is not None:
            with open(temp_save_path, 'wb') as temp_file:
                temp_file.write(contents)
        else:
            raise ValueError("Either path or contents must be provided")

        self.save_dir = path.parent if path is not None else None
        self.sqlite_db = temp_save_path

        self.save_context = save_context

        conn_str = f"file:{temp_save_path}?mode={'ro' if read_only else 'rw'}"
        # check_same_thread=False allows connection to be used from multiple threads
        # This is safe for read operations in parallel parsing
        self.connection = sqlite3.connect(conn_str, uri=True, check_same_thread=False)

        self.list_all_items_in_db()
        self.read_header()

    def set_max_workers(self, max_workers: int):
        """Set maximum workers for parallel parsing. Only applicable if GIL is disabled."""
        if not _PARALLEL_ENABLED:
            ArkSaveLogger.warning_log("Parallel parsing is not enabled (GIL is active), set_max_workers has no effect.")
            return
        self._max_workers = max_workers

    def __del__(self):
        self.close()

        # clean up temp file
        if self.sqlite_db is not None and self.sqlite_db.exists():
            try:
                self.sqlite_db.unlink()
            except PermissionError:
                pass  # File still locked by SQLite, will be cleaned up later

    def get_bytes(self) -> Optional[bytes]:
        if self.sqlite_db is not None and self.sqlite_db.exists():
            with open(self.sqlite_db, 'rb') as file:
                return file.read()
        return None

    def read_table(self, header_data: 'ArkBinaryParser') -> Dict[int, str]:
        count = header_data.read_int()
        self.name_count = count
        ArkSaveLogger.set_file(header_data, "name_table.bin")

        result = {}
        try:
            for _ in range(count):
                key = header_data.read_uint32()
                result[key] = header_data.read_string()
            self.last_name_end = header_data.position
        except Exception as e:
            ArkSaveLogger.error_log(f"Error reading name table: {e}")
            ArkSaveLogger.open_hex_view(True)
            raise e
        return result

    def read_header(self):
        header_data = self.get_custom_value("SaveHeader")
        ArkSaveLogger.set_file(header_data, "header.bin")

        self.save_context.save_version = header_data.read_short()
        ArkSaveLogger.save_log(f"Save version: {self.save_context.save_version}")

        if self.save_context.save_version >= 14:
            ArkSaveLogger.save_log(f"V14 unknown value 1: {header_data.read_uint32()}")
            ArkSaveLogger.save_log(f"V14 unknown value 2: {header_data.read_uint32()}")

        name_table_offset = header_data.read_int()
        self.name_offset = name_table_offset
        ArkSaveLogger.save_log(f"Name table offset: {name_table_offset}")
        self.save_context.game_time = header_data.read_double()
        ArkSaveLogger.save_log(f"Game time: {self.save_context.game_time}")

        if self.save_context.save_version >= 12:
            self.save_context.unknown_value = header_data.read_uint32()
            ArkSaveLogger.save_log(f"Unknown value: {self.save_context.unknown_value}")

        self.save_context.sections = SaveConnection.read_locations(header_data)

        header_data.set_position(30)
        self.save_context.map_name = header_data.read_string()

        # check_uint64(header_data, 0)
        header_data.set_position(name_table_offset)
        self.save_context.set_names(self.read_table(header_data))

    def read_actor_locations(self):
        actor_transforms = self.get_custom_value("ActorTransforms")
        ArkSaveLogger.save_log("Actor transforms table retrieved")
        if actor_transforms:
            at, atp = actor_transforms.read_actor_transforms()
            self.save_context.actor_transforms = at
            self.save_context.actor_transform_positions = atp
        # print(f"Length of actor transforms: {len(self.save_context.actor_transforms)}")

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def cache_all_classes(self):
        """Bulk pre-cache UUID -> class_name for all objects in DB.
        Call before parallel parsing to avoid SQLite lock contention."""
        if self._class_cache:
            return
        query = "SELECT key, value FROM game"
        with self._db_lock:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
        for key_bytes, value_bytes in rows:
            obj_uuid = _fast_uuid_from_bytes(key_bytes)
            try:
                reader = ArkBinaryParser(value_bytes, self.save_context)
                class_name, _ = ArkGameObject.read_name(obj_uuid, reader)
                self._class_cache[obj_uuid] = class_name
            except Exception:
                pass

    def get_class_of_uuid(self, obj_uuid: uuid.UUID) -> Optional[str]:
        if obj_uuid in self._class_cache:
            return self._class_cache[obj_uuid]
        bin = self.get_game_obj_binary(obj_uuid)
        reader = ArkBinaryParser(bin, self.save_context)
        class_name, string_name = ArkGameObject.read_name(obj_uuid, reader)
        self._class_cache[obj_uuid] = class_name
        return class_name

    def list_all_items_in_db(self):
        query = "SELECT key, value FROM game"
        with self.connection as conn:
            cursor = conn.execute(query)
            name = cursor.description
            rowCount = 0
            for row in cursor:
                rowCount += 1
            ArkSaveLogger.save_log(f"Found {rowCount} items in game table")

        # get custom values
        query = "SELECT key, value FROM custom"
        with self.connection as conn:
            cursor = conn.execute(query)
            for row in cursor:
                ArkSaveLogger.save_log(f"Custom key: {row[0]}")

    def add_name_to_name_table(self, name: str, id: Optional[int] = None):
        header_data = self.get_custom_value("SaveHeader")
        self.name_count += 1
        header_data.set_position(self.name_offset)
        header_data.replace_bytes(self.name_count.to_bytes(4, byteorder="little"))
        header_data.set_position(self.last_name_end)
        new_id = self.save_context.add_new_name(name, id)
        header_data.insert_uint32(new_id)
        header_data.insert_string(name)
        self.last_name_end = header_data.position

        # store new name table
        query = "UPDATE custom SET value = ? WHERE key = 'SaveHeader'"
        with self.connection as conn:
            conn.execute(query, (header_data.byte_buffer,))
            conn.commit()

        return new_id

    def find_value_in_game_table_objects(self, value: bytes):
        query = "SELECT key, value FROM game"
        cursor = self.connection.cursor()
        cursor.execute(query)
        for row in cursor:
            reader = ArkBinaryParser(row[1], self.save_context)
            result = reader.find_byte_sequence(value, adjust_offset=0)

            for r in result:
                print(f"Found at {row[0]}, index: {r}")

                obj = self.get_game_object_by_id(SaveConnection.byte_array_to_uuid(row[0]))
                if obj:
                    print(f"Object: {obj.blueprint} ({obj.uuid})")

    def find_value_in_custom_tables(self, value: bytes):
        query = "SELECT key, value FROM custom"
        cursor = self.connection.cursor()
        cursor.execute(query)
        for row in cursor:
            reader = ArkBinaryParser(row[1], self.save_context)
            result = reader.find_byte_sequence(value, adjust_offset=0)

            for r in result:
                print(f"Found at {row[0]}, index: {r}")

    def replace_value_in_custom_tables(self, search: bytes, replace: bytes):
        query = "SELECT key, value FROM custom"
        cursor = self.connection.cursor()
        cursor.execute(query)
        for row in cursor:
            reader = ArkBinaryParser(row[1], self.save_context)
            result = reader.find_byte_sequence(search, adjust_offset=0)

            for r in result:
                print(f"Found at {row[0]}, index: {r}")
                reader.set_position(r)
                reader.replace_bytes(replace)

                query = "UPDATE custom SET value = ? WHERE key = ?"
                with self.connection as conn:
                    conn.execute(query, (reader.byte_buffer, row[0]))
                    conn.commit()

    def get_obj_uuids(self) -> Collection[uuid.UUID]:
        query = "SELECT key FROM game"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return [SaveConnection.byte_array_to_uuid(row[0]) for row in cursor]

    def print_tables_and_sizes(self):
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        cursor = self.connection.cursor()
        cursor.execute(query)
        for row in cursor:
            table_name = row[0]
            query = f"SELECT COUNT(*) FROM {table_name}"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"Table {table_name} has {count} rows")

    def print_custom_table_sizes(self):
        query = "SELECT key, LENGTH(value) FROM custom"
        cursor = self.connection.cursor()
        cursor.execute(query)
        for row in cursor:
            print(f"Key: {row[0]}, size: {row[1]}")

    def add_obj_to_db(self, obj_uuid: uuid.UUID, obj_data: bytes):
        query = "INSERT INTO game (key, value) VALUES (?, ?)"
        with self.connection as conn:
            conn.execute(query, (SaveConnection.uuid_to_byte_array(obj_uuid), obj_data))
            conn.commit()

        self.get_game_object_by_id(obj_uuid, reparse=True)

    def modify_game_obj(self, obj_uuid: uuid.UUID, obj_data: bytes):
        query = "UPDATE game SET value = ? WHERE key = ?"
        with self.connection as conn:
            conn.execute(query, (obj_data, SaveConnection.uuid_to_byte_array(obj_uuid)))
            conn.commit()

        self.get_game_object_by_id(obj_uuid, reparse=True)

    def remove_obj_from_db(self, obj_uuid: uuid.UUID):
        try:
            query = "DELETE FROM game WHERE key = ?"
            with self.connection as conn:
                conn.execute(query, (SaveConnection.uuid_to_byte_array(obj_uuid),))
                conn.commit()
        except Exception as e:
            ArkSaveLogger.error_log(f"Error removing object {obj_uuid} from database: {e}")

        if obj_uuid in self.parsed_objects:
            self.parsed_objects.pop(obj_uuid)

    def add_actor_transform(self, uuid: uuid.UUID, binary_data: bytes, no_store: bool = False):
        actor_transforms = self.get_custom_value("ActorTransforms")

        # print(f"Adding actor transform {uuid}")

        if actor_transforms:
            actor_transforms.set_position(actor_transforms.size() - 16)
            actor_transforms.insert_bytes(SaveConnection.uuid_to_byte_array(uuid))
            actor_transforms.set_position(actor_transforms.size() - 16)
            actor_transforms.insert_bytes(binary_data)
            # print(f"New size: {actor_transforms.size()}")

            query = "UPDATE custom SET value = ? WHERE key = 'ActorTransforms'"
            with self.connection as conn:
                conn.execute(query, (actor_transforms.byte_buffer,))
                conn.commit()

    def add_actor_transforms(self, new_actor_transforms: bytes):
        actor_transforms = self.get_custom_value("ActorTransforms")
        if actor_transforms:
            actor_transforms.set_position(actor_transforms.size() - 16)
            actor_transforms.insert_bytes(new_actor_transforms)

            query = "UPDATE custom SET value = ? WHERE key = 'ActorTransforms'"
            with self.connection as conn:
                conn.execute(query, (actor_transforms.byte_buffer,))
                conn.commit()

    def modify_actor_transform(self, uuid: uuid.UUID, binary_data: bytes):
        actor_transforms = self.get_custom_value("ActorTransforms")

        if actor_transforms:
            byte_sequence = SaveConnection.uuid_to_byte_array(uuid)
            ArkSaveLogger.save_log(f"Modifying actor transform for {uuid} ...")
            positions = actor_transforms.find_byte_sequence(byte_sequence, adjust_offset=0)
            ArkSaveLogger.save_log(f"Found positions: {positions}")
            if len(positions) > 1:
                ArkSaveLogger.warning_log(f"Multiple actor transforms found for {uuid}, modifying the first one.")
            if len(positions) == 0:
                ArkSaveLogger.error_log(f"No actor transform found for {uuid}, cannot modify.")
                return
            actor_transforms.set_position(positions[0])
            actor_transforms.replace_bytes(byte_sequence + binary_data)

            query = "UPDATE custom SET value = ? WHERE key = 'ActorTransforms'"
            with self.connection as conn:
                conn.execute(query, (actor_transforms.byte_buffer,))

    def store_db(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        new_conn = sqlite3.connect(path)
        try:
            self.connection.backup(new_conn)
        finally:
            new_conn.close()

        print(f"Database successfully backed up to {path}")

    def get_save_binary_size(self) -> int:
        query = "SELECT SUM(LENGTH(value)) FROM game"
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        if result and result[0]:
            return result[0]
        return 0

    def get_all_present_classes(self):
        query = "SELECT value FROM game"
        classes = []
        with self.connection as conn:
            cursor = conn.execute(query)
            for row in cursor:
                byte_buffer = ArkBinaryParser(row[0], self.save_context)
                class_name = byte_buffer.read_name()
                if class_name not in classes:
                    classes.append(class_name)
        return classes

    def get_custom_value(self, key: str) -> Optional['ArkBinaryParser']:
        query = f"SELECT value FROM custom WHERE key = ? LIMIT 1"
        cursor = self.connection.cursor()
        cursor.execute(query, (key,))
        row = cursor.fetchone()
        if row:
            return ArkBinaryParser(row[0], self.save_context)
        return None

    def get_game_obj_binary(self, obj_uuid: uuid.UUID) -> Optional[bytes]:
        query = "SELECT value FROM game WHERE key = ?"
        with self._db_lock:
            cursor = self.connection.cursor()
            cursor.execute(query, (SaveConnection.uuid_to_byte_array(obj_uuid),))
            row = cursor.fetchone()
        if not row:
            raise ValueError(f"Object with UUID {obj_uuid} not found in database")

        return row[0]

    def get_parser_for_game_object(self, obj_uuid: uuid.UUID) -> Optional[ArkBinaryParser]:
        binary = self.get_game_obj_binary(obj_uuid)
        if binary is None:
            return None
        return ArkBinaryParser(binary, self.save_context)

    def is_in_db(self, obj_uuid: uuid.UUID) -> bool:
        # Check caches first to avoid SQLite lock contention
        if obj_uuid in self.parsed_objects:
            return True
        if obj_uuid in self._class_cache:
            return True
        query = "SELECT key FROM game WHERE key = ?"
        with self._db_lock:
            cursor = self.connection.cursor()
            cursor.execute(query, (SaveConnection.uuid_to_byte_array(obj_uuid),))
            result = cursor.fetchone() is not None
        return result

    def get_game_object_by_id(self, obj_uuid: uuid.UUID, reparse: bool = False) -> Optional['ArkGameObject']:
        if obj_uuid in self.parsed_objects and not reparse:
            return self.parsed_objects[obj_uuid]
        bin = self.get_game_obj_binary(obj_uuid)
        reader = ArkBinaryParser(bin, self.save_context)

        class_name, string_name = ArkGameObject.read_name(obj_uuid, reader)

        obj = SaveConnection.parse_as_predefined_object(obj_uuid, class_name, reader)

        if obj:
            self.parsed_objects[obj_uuid] = obj

        return obj

    def get_game_objects(self, reader_config: GameObjectReaderConfiguration = GameObjectReaderConfiguration()) -> Dict[uuid.UUID, 'ArkGameObject']:
        query = "SELECT key, value FROM game"
        game_objects = {}
        objects = []
        prop_ids = []

        for prop in reader_config.property_names:
            id_ = self.save_context.get_name_id(prop)
            if id_ is not None:
                prop_ids.append(id_.to_bytes(4, byteorder="little") + b'\x00\x00\x00\x00')

        ArkSaveLogger.enter_struct("GameObjects")

        # Collect items from SQLite (single-threaded due to SQLite constraints)
        items_to_parse: List[Tuple[UUID, str, bytes]] = []
        
        with self.connection as conn:   
            cursor = conn.execute(query)
            for row in cursor:
                obj_uuid = self.byte_array_to_uuid(row[0])
                binary_data = row[1]
                self.save_context.all_uuids.append(obj_uuid)
                
                if reader_config.uuid_filter and not reader_config.uuid_filter(obj_uuid):
                    continue

                byte_buffer = ArkBinaryParser(binary_data, self.save_context)
                class_name, _ = ArkGameObject.read_name(obj_uuid, byte_buffer)

                if reader_config.blueprint_name_filter and not reader_config.blueprint_name_filter(class_name):
                    continue

                if SaveConnection.failed_parses.get(class_name, 0) >= 5:
                    if SaveConnection.failed_parses[class_name] == 5:
                        ArkSaveLogger.warning_log(f"Skipping parsing of class {class_name} due to previous errors")
                    SaveConnection.failed_parses[class_name] += 1
                    self.faulty_objects += 1
                    continue

                if class_name not in objects:
                    objects.append(class_name)
                
                if obj_uuid in self.parsed_objects:
                    found = len(prop_ids) == 0
                    for prop in reader_config.property_names:
                        if self.parsed_objects[obj_uuid].has_property(prop):
                            found = True
                            break
                    if found:
                        game_objects[obj_uuid] = self.parsed_objects[obj_uuid]
                    continue
                
                found = len(prop_ids) == 0 or contains_any_pattern(binary_data, prop_ids)
                if found:
                    items_to_parse.append((obj_uuid, class_name, binary_data))

        ArkSaveLogger.exit_struct()

        # Parse objects - parallel when GIL disabled, sequential otherwise
        if items_to_parse:
            if _PARALLEL_ENABLED and self._max_workers > 1:
                # Parallel parsing with _max_workers (optimal for free-threaded Python)
                ArkSaveLogger.save_log(f"Parsing {len(items_to_parse)} objects with {self._max_workers} workers...")
                ctx = self.save_context
                _worker_initialized = threading.local()
                
                def parse_item(item: Tuple[UUID, str, bytes]) -> Tuple[UUID, Optional[ArkGameObject]]:
                    # Mark this thread as a worker (once per thread)
                    if not getattr(_worker_initialized, 'done', False):
                        mark_as_worker_thread()
                        _worker_initialized.done = True
                    obj_uuid, class_name, binary_data = item
                    obj = _parse_single_object(obj_uuid, class_name, binary_data, ctx)
                    return obj_uuid, obj
                
                with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                    results = list(executor.map(parse_item, items_to_parse))
                
                for obj_uuid, obj in results:
                    if obj:
                        game_objects[obj_uuid] = obj
                        self.parsed_objects[obj_uuid] = obj
                        self.nr_parsed += 1
                    else:
                        self.faulty_objects += 1
            else:
                # Sequential parsing (GIL enabled)
                for obj_uuid, class_name, binary_data in items_to_parse:
                    byte_buffer = ArkBinaryParser(binary_data, self.save_context)
                    ark_game_object = self.parse_as_predefined_object(obj_uuid, class_name, byte_buffer)
                    
                    if ark_game_object:
                        game_objects[obj_uuid] = ark_game_object
                        self.parsed_objects[obj_uuid] = ark_game_object
                        self.nr_parsed += 1
                        if self.nr_parsed % 25000 == 0:
                            ArkSaveLogger.save_log(f"Nr parsed: {self.nr_parsed}")
                    else:
                        self.faulty_objects += 1
        
        if self.faulty_objects > 0:
            ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.ERROR, True)
            ArkSaveLogger.error_log(f"{self.faulty_objects} objects could not be parsed, if possible, please report this to the developers.")
            ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.ERROR, False)
        
        return game_objects

    def reset_caching(self):
        self.parsed_objects.clear()

    @staticmethod
    def read_locations(header_data: 'ArkBinaryParser') -> list:
        parts = []

        num_parts = header_data.read_uint32()
        ArkSaveLogger.save_log(f"Number of header locations: {num_parts}")

        for _ in range(num_parts):
            part = header_data.read_string()
            if not part.endswith("_WP"):
                parts.append(HeaderLocation(part))
            header_data.validate_uint32(0xFFFFFFFF)
        return parts

    @staticmethod
    def byte_array_to_uuid(byte_array: bytes) -> uuid.UUID:
        return _fast_uuid_from_bytes(byte_array)

    @staticmethod
    def uuid_to_byte_array(obj_uuid: uuid.UUID) -> bytes:
        return obj_uuid.bytes

    @staticmethod
    def parse_as_predefined_object(obj_uuid, class_name, byte_buffer: ArkBinaryParser):
        try:
            return ArkGameObject(obj_uuid, class_name, byte_buffer)
        except Exception as e:
            reraise = False
            if "/Game/" in class_name or "/Script/" in class_name:
                if ArkSaveLogger._allow_invalid_objects is False:
                    byte_buffer.find_names(type=2)
                    byte_buffer.structured_print(to_default_file=True)
                    ArkSaveLogger.error_log(f"Error parsing object {obj_uuid} of type {class_name}: {e}")
                    reraise = True
                
                ArkSaveLogger.warning_log(f"Error parsing object {obj_uuid} of type {class_name}, skipping...")
            else:
                byte_buffer.structured_print(to_default_file=True)
                ArkSaveLogger.warning_log(f"Error parsing non-standard object of type {class_name}")

                # input("Press Enter to continue...")

            SaveConnection.failed_parses[class_name] = SaveConnection.failed_parses.get(class_name, 0) + 1
            ArkSaveLogger.warning_log(f"Failed parses for this class: {SaveConnection.failed_parses[class_name]}")

            if SaveConnection.failed_parses[class_name] == 1:
                ArkSaveLogger.error_log("Reparsing with logging:")
                ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.PARSER, True)
                try:
                    ArkGameObject(obj_uuid, class_name, byte_buffer)
                except Exception as _:
                    ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.PARSER, False)
                    ArkSaveLogger.open_hex_view(True)

            if reraise:
                raise Exception(f"Error parsing object {obj_uuid} of type {class_name}: {e}")
        finally:
            ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.PARSER, False)
            
        return None