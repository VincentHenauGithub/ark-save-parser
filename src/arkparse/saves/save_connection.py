import sqlite3
import uuid
from pathlib import Path
from typing import Collection, Optional, Dict

from arkparse.logging import ArkSaveLogger
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser, GameObjectReaderConfiguration
from arkparse.saves.header_location import HeaderLocation
from arkparse.saves.save_context import SaveContext
from arkparse.utils import TEMP_FILES_DIR

class SaveConnection:

    name_offset = 0
    name_count = 0
    last_name_end = 0

    nr_parsed = 0
    faulty_objects = 0

    def __init__(self, save_context: SaveContext, path: Path = None, contents: bytes = None, read_only: bool = False):

        # create temp copy of file
        temp_save_path = TEMP_FILES_DIR / (str(uuid.uuid4()) + ".ark")
        self.parsed_objects: Dict[uuid.UUID, ArkGameObject] = {}

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
        self.connection = sqlite3.connect(conn_str, uri=True)

        self.list_all_items_in_db()
        self.read_header()

    def __del__(self):
        self.close()

        # clean up temp file
        if self.sqlite_db is not None and self.sqlite_db.exists():
            self.sqlite_db.unlink()

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
        self.save_context.names = self.read_table(header_data)

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
        header_data.insert_uint32(self.save_context.add_new_name(name, id))
        header_data.insert_string(name)
        self.last_name_end = header_data.position

        # store new name table
        query = "UPDATE custom SET value = ? WHERE key = 'SaveHeader'"
        with self.connection as conn:
            conn.execute(query, (header_data.byte_buffer,))
            conn.commit()

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
        with sqlite3.connect(path) as new_conn:
            self.connection.backup(new_conn)

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
        query = "SELECT key FROM game WHERE key = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (SaveConnection.uuid_to_byte_array(obj_uuid),))
        return cursor.fetchone() is not None

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
        row_index = 0
        objects = []
        prop_ids = []

        for prop in reader_config.property_names:
            id_ = self.save_context.get_name_id(prop)
            if id_ is not None:
                prop_ids.append(id_.to_bytes(4, byteorder="little") + b'\x00\x00\x00\x00')

        ArkSaveLogger.enter_struct("GameObjects")

        with self.connection as conn:   
            cursor = conn.execute(query)
            for row in cursor:
                if row_index < 0:
                    row_index += 1
                    self.nr_parsed += 1
                    continue

                obj_uuid = self.byte_array_to_uuid(row[0])
                self.save_context.all_uuids.append(obj_uuid)
                if reader_config.uuid_filter and not reader_config.uuid_filter(obj_uuid):
                    ArkSaveLogger.save_log("Skipping object %s", obj_uuid)
                    ArkSaveLogger.exit_struct()
                    continue

                byte_buffer = ArkBinaryParser(row[1], self.save_context)
                ArkSaveLogger.set_file(byte_buffer, "game_object.bin")
                class_name, string_name =  ArkGameObject.read_name(obj_uuid, byte_buffer)
                ArkSaveLogger.enter_struct(class_name)

                if reader_config.blueprint_name_filter and not reader_config.blueprint_name_filter(class_name):
                    ArkSaveLogger.exit_struct()
                    continue

                if class_name not in objects:
                    objects.append(class_name)
                
                if obj_uuid not in self.parsed_objects.keys():
                    ark_game_object = None
                    found = False
                    for pid in prop_ids:
                        if byte_buffer.find_byte_sequence(pid, adjust_offset=0):
                            found = True

                    if found or len(prop_ids) == 0:
                        ark_game_object = self.parse_as_predefined_object(obj_uuid, class_name, byte_buffer)

                        if ark_game_object:
                            game_objects[obj_uuid] = ark_game_object
                            self.parsed_objects[obj_uuid] = ark_game_object

                            self.nr_parsed += 1
                            if self.nr_parsed % 25000 == 0:
                                ArkSaveLogger.save_log(f"Nr parsed: {self.nr_parsed}")
                        else:
                            self.faulty_objects += 1
                else:
                    found = False or (len(prop_ids) == 0)
                    for prop in reader_config.property_names:
                        if self.parsed_objects[obj_uuid].has_property(prop):
                            found = True

                    if found:
                        game_objects[obj_uuid] = self.parsed_objects[obj_uuid]
        
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
        return uuid.UUID(bytes=byte_array)

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