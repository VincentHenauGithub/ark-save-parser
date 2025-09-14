import math
from pathlib import Path
from typing import Dict, Optional, Collection
import uuid

from arkparse.logging import ArkSaveLogger

from arkparse.parsing.game_object_reader_configuration import GameObjectReaderConfiguration
from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase

from arkparse.object_model.ark_game_object import ArkGameObject
from .save_connection import SaveConnection
from .save_context import SaveContext

class AsaSave:
    # Populate manually if constructor parameter use_connection is False
    parsed_objects: Dict[uuid.UUID, ArkGameObject] = {}

    def __init__(self, path: Path = None, contents: bytes = None, read_only: bool = False, use_connection: bool = True):

        self.save_context = SaveContext()

        # Populate manually if constructor parameter use_connection is False
        self.custom_value_GameModeCustomBytes: Optional['ArkBinaryParser'] = None
        self.custom_value_SaveHeader: Optional['ArkBinaryParser'] = None
        self.custom_value_ActorTransforms: Optional['ArkBinaryParser'] = None
        self.game_obj_binaries: Optional['Dict[uuid.UUID, Optional[bytes]]'] = None
        self.all_classes: Optional['list[str]'] = None
        self.containers: Optional[Dict[uuid.UUID, ArkGameObject]] = None

        self.profile_data_in_db = False
        self.save_dir = path.parent if path is not None else None
        self.save_connection = None
        if use_connection:
            self.save_connection = SaveConnection(save_context=self.save_context, path=path, contents=contents, read_only=read_only)
            self.initialize()

    def __del__(self):
        self.close()

    @property
    def faulty_objects(self) -> Dict[uuid.UUID, ArkGameObject]:
        if self.save_connection is not None:
            return self.save_connection.faulty_objects
        return 0

    def initialize(self):
        self.read_actor_locations()
        self.profile_data_in_db = self.profile_data_in_saves()
        self._get_game_time_params()

    def profile_data_in_saves(self) -> bool:
        parser: ArkBinaryParser = self.get_custom_value("GameModeCustomBytes")
        if len(parser.byte_buffer) < 30:
            ArkSaveLogger.save_log("GameModeCustomBytes is too short, profile data not in saves")
            return False
        return True

    def _get_game_time_params(self):
        config: GameObjectReaderConfiguration = GameObjectReaderConfiguration()
        config.blueprint_name_filter = lambda name: name is not None and "daycycle" in name.lower()

        objs = self.get_game_objects(config)

        current_time = 0
        current_day = 0

        for _, obj in objs.items():
            day_id = obj.get_property_value("theDayNumberToMakeSerilizationWork", None)
            if day_id is not None:
                current_day = day_id
                current_time = obj.get_property_value("CurrentTime", 0)
                break

        self.save_context.current_time = current_time
        self.save_context.current_day = current_day

        ArkSaveLogger.save_log(f"Current time: {self.save_context.current_time}, current day: {self.save_context.current_day}")

    def get_game_time_readable_string(self):
        current_hours = str(max(0, math.floor(self.save_context.current_time / 3600)))
        if len(current_hours) < 2:
            current_hours = f"0{current_hours}"
        remaining: float = (self.save_context.current_time % 3600)
        current_minutes = str(max(0, math.floor(remaining / 60)))
        if len(current_minutes) < 2:
            current_minutes = f"0{current_minutes}"
        current_seconds = str(max(0, math.floor(remaining % 60)))
        if len(current_seconds) < 2:
            current_seconds = f"0{current_seconds}"
        return f"Day {self.save_context.current_day}, {current_hours}:{current_minutes}:{current_seconds}"
    
    def get_container_of_inventory(self, inv_uuid: uuid.UUID) -> ArkGameObject:
        if self.containers is None:
            ArkSaveLogger.save_log("Fetching all containers with MyInventoryComponent property")
            config = GameObjectReaderConfiguration()
            config.property_names = ["MyInventoryComponent"]
            self.containers = self.get_game_objects(config)

        for _, container in self.containers.items():
            # print(container.get_short_name())
            if container.get_property_value("MyInventoryComponent") is not None and uuid.UUID(container.get_property_value("MyInventoryComponent").value) == inv_uuid:
                return container
        return None

    def read_actor_locations(self):
        actor_transforms = self.get_custom_value("ActorTransforms")
        ArkSaveLogger.save_log("Actor transforms table retrieved")
        if actor_transforms:
            at, atp = actor_transforms.read_actor_transforms()
            self.save_context.actor_transforms = at
            self.save_context.actor_transform_positions = atp
        # print(f"Length of actor transforms: {len(self.save_context.actor_transforms)}")

    def get_actor_transform(self, uuid: uuid.UUID):
        if uuid in self.save_context.actor_transforms:
            return self.save_context.actor_transforms[uuid]
        ArkSaveLogger.error_log(f"Actor transform for {uuid} not found")
        return None

    def find_in_header(self, byte_sequence: bytes) -> Optional[int]:
        header_data = self.get_custom_value("SaveHeader")
        if not header_data:
            return None

        positions = header_data.find_byte_sequence(byte_sequence, adjust_offset=0)
        if not positions:
            print(f"Byte sequence {byte_sequence} not found in header")
            return None

        ArkSaveLogger.save_log(f"Found byte sequence in header at position {positions}")
        header_data.set_position(positions[0])
        ArkSaveLogger.set_file(header_data, "header.bin")
        ArkSaveLogger.open_hex_view(True)
        return None

    def add_name_to_name_table(self, name: str):
        if self.save_connection is not None:
            self.save_connection.add_name_to_name_table(name)

    def get_parser_for_game_object(self, obj_uuid: uuid.UUID) -> Optional[ArkBinaryParser]:
        if self.game_obj_binaries is not None and obj_uuid in self.game_obj_binaries:
            return ArkBinaryParser(self.game_obj_binaries[obj_uuid], self.save_context)
        if self.save_connection is not None:
            return self.save_connection.get_parser_for_game_object(obj_uuid)
        return None
    
    def find_value_in_game_table_objects(self, value: bytes):
        if self.save_connection is not None:
            self.save_connection.find_value_in_game_table_objects(value)
            
    def find_value_in_custom_tables(self, value: bytes):
        if self.save_connection is not None:
            self.save_connection.find_value_in_custom_tables(value)

    def replace_value_in_custom_tables(self, search: bytes, replace: bytes):
        if self.save_connection is not None:
            self.save_connection.replace_value_in_custom_tables(search, replace)

    def get_obj_uuids(self) -> Collection[uuid.UUID]:
        return self.get_obj_uuids()
    
    def print_tables_and_sizes(self):
        if self.save_connection is not None:
            self.save_connection.print_tables_and_sizes()

    def print_custom_table_sizes(self):
        if self.save_connection is not None:
            self.save_connection.print_custom_table_sizes()
    
    def is_in_db(self, obj_uuid: uuid.UUID) -> bool:
        if self.game_obj_binaries is not None and obj_uuid in self.game_obj_binaries:
            return True
        if self.save_connection is not None:
            return self.save_connection.is_in_db(obj_uuid)
        return False
    
    def add_to_db(self, obj: ParsedObjectBase):
        self.add_obj_to_db(obj.object.uuid, obj.binary.byte_buffer)
        
    def add_obj_to_db(self, obj_uuid: uuid.UUID, obj_data: bytes):
        if self.save_connection is not None:
            self.save_connection.add_obj_to_db(obj_uuid, obj_data)

    def modify_game_obj(self, obj_uuid: uuid.UUID, obj_data: bytes):
        if self.save_connection is not None:
            self.save_connection.modify_game_obj(obj_uuid, obj_data)

    def remove_obj_from_db(self, obj_uuid: uuid.UUID):
        if self.save_connection is not None:
            self.save_connection.remove_obj_from_db(obj_uuid)

    def add_actor_transform(self, uuid: uuid.UUID, binary_data: bytes, no_store: bool = False):
        if self.save_connection is not None:
            self.save_connection.add_actor_transform(uuid, binary_data, no_store)

    def add_actor_transforms(self, new_actor_transforms: bytes):
        if self.save_connection is not None:
            self.save_connection.add_actor_transforms(new_actor_transforms)

    def modify_actor_transform(self, uuid: uuid.UUID, binary_data: bytes):
        if self.save_connection is not None:
            self.save_connection.modify_actor_transform(uuid, binary_data)

    def store_db(self, path: Path):
        if self.save_connection is not None:
            self.save_connection.store_db(path)

    def get_save_binary_size(self) -> int:
        if self.save_connection is not None:
            return self.save_connection.get_save_binary_size()
        return 0

    def reset_caching(self):
        self.parsed_objects.clear()
        if self.save_connection is not None:
            self.save_connection.reset_caching()

    def get_game_objects(self, reader_config: GameObjectReaderConfiguration = GameObjectReaderConfiguration()) -> Dict[uuid.UUID, 'ArkGameObject']:
        if self.parsed_objects is not None and len(self.parsed_objects) > 0:
            return self.parsed_objects
        else:
            if self.save_connection is not None:
                return self.save_connection.get_game_objects(reader_config)
            return {}
    
    def get_all_present_classes(self):
        if self.all_classes is not None:
            return self.all_classes
        else:
            if self.save_connection is not None:
                return self.save_connection.get_all_present_classes()
            return None

    def get_game_object_by_id(self, obj_uuid: uuid.UUID, reparse: bool = False) -> Optional['ArkGameObject']:
        if obj_uuid in self.parsed_objects and not reparse:
            return self.parsed_objects[obj_uuid]
        else:
            if self.game_obj_binaries is not None and obj_uuid in self.game_obj_binaries:
                bin = self.game_obj_binaries[obj_uuid]
                reader = ArkBinaryParser(bin, self.save_context)
                obj = SaveConnection.parse_as_predefined_object(obj_uuid, reader.read_name(), reader)
                if obj:
                    self.parsed_objects[obj_uuid] = obj
                return obj
            else:
                if self.save_connection is not None:
                    return self.save_connection.get_game_object_by_id(obj_uuid, reparse)
                return None

    def get_custom_value(self, key: str) -> Optional['ArkBinaryParser']:
        if "GameModeCustomBytes" in key and self.custom_value_GameModeCustomBytes is not None:
            return self.custom_value_GameModeCustomBytes
        if "SaveHeader" in key and self.custom_value_SaveHeader is not None:
            return self.custom_value_SaveHeader
        if "ActorTransforms" in key and self.custom_value_ActorTransforms is not None:
            return self.custom_value_ActorTransforms

        if self.save_connection is not None:
            return self.save_connection.get_custom_value(key)
        return None

    def close(self):
        if self.save_connection is not None:
            self.save_connection.close()