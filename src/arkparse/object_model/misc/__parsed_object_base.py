from ..ark_game_object import ArkGameObject
from uuid import UUID, uuid4
import json
from arkparse.parsing import ArkBinaryParser
from pathlib import Path
from arkparse.logging import ArkSaveLogger
from importlib.resources import files
from typing import Dict, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from arkparse import AsaSave

class ParsedObjectBase:
    binary: ArkBinaryParser = None
    object: ArkGameObject = None
    props_initialized: bool = False
    save: "AsaSave" = None

    @property
    def uuid(self) -> UUID:
        return self.object.uuid if self.object is not None else None
    
    @property
    def blueprint(self) -> str:
        return self.object.blueprint if self.object is not None else None

    def __init_props__(self):
        pass

    def __init__(self, uuid: UUID = None, save: "AsaSave" = None):
        if uuid is None or save is None:
            return

        self.save = save
        if not save.is_in_db(uuid):
            ArkSaveLogger.error_log(f"Could not find binary for game object {uuid} in save")
        else:
            self.binary = save.get_parser_for_game_object(uuid)
            self.object = save.get_game_object_by_id(uuid)

        self.__init_props__()

    @staticmethod
    def _generate(save: "AsaSave", template_path: str):
        package = 'arkparse.assets'
        path = files(package) / template_path
        name_path = files(package) / (template_path + "_n.json")
        bin = path.read_bytes()
        names: Dict[int, str] = json.loads(name_path.read_text())
        parser = ArkBinaryParser(bin, save.save_context)
        new_uuid = uuid4()
        parser.replace_name_ids(names, save)
        save.add_obj_to_db(new_uuid, parser.byte_buffer)
        return new_uuid, parser

    def reidentify(self, new_uuid: UUID = None, update=True):
        self.replace_uuid(new_uuid=new_uuid)
        self.renumber_name()
        uuid = new_uuid if new_uuid is not None else self.object.uuid

        # creation_time = self.object.find_property("OriginalCreationTime")
        # if creation_time is not None:
        #     self.binary.replace_double(creation_time, self.save.save_context.game_time)

        self.object = ArkGameObject(uuid=uuid, blueprint=self.object.blueprint, binary_reader=self.binary)

        if update:
            self.update_binary()

    def replace_uuid(self, new_uuid: UUID = None, uuid_to_replace: UUID = None):
        if new_uuid is  None:
            new_uuid = uuid4()
        
        uuid_as_bytes = new_uuid.bytes           
        old_uuid_bytes = self.object.uuid.bytes if uuid_to_replace is None else uuid_to_replace.bytes
        self.binary.byte_buffer = self.binary.byte_buffer.replace(old_uuid_bytes, uuid_as_bytes)

        if uuid_to_replace is None:
            self.object.uuid = new_uuid

    def renumber_name(self, new_number: bytes = None):
        self.binary.byte_buffer = self.object.re_number_names(self.binary, new_number)

    def replace_name_at_index_with(self, index: int, new_name: str):
        if self.object is None:
            ArkSaveLogger.error_log("This object has no ArkGameObject associated with it, cannot replace name")
            return

        if index < 0 or index >= len(self.object.name_metadata):
            ArkSaveLogger.error_log(f"Index {index} out of bounds for name metadata")
            return

        md = self.object.name_metadata[index]
        new_bytes = new_name.encode("utf-8")
        self.binary.replace_bytes(new_bytes, md.offset, md.length)

    def store_binary(self, path: Path, name: str = None, prefix: str = "obj_", no_suffix= False):
        name = name if name is not None else str(self.object.uuid)
        file_path = path / (f"{prefix}{name}.bin" if not no_suffix else f"{prefix}{name}")
        name_path = path / (f"{prefix}{name}_n.json")

        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as file:
            file.write(self.binary.byte_buffer)

        with open(name_path, "w") as file:
            json.dump(self.binary.find_names(), file, indent=4)

    def update_binary(self):

        if self.object is None:
            ArkSaveLogger.error_log("This object has no ArkGameObject associated with it, cannot update binary as not in save")
            return
        if self.save is not None:
            self.save.modify_game_obj(self.object.uuid, self.binary.byte_buffer)
        else:
            ArkSaveLogger.error_log("Parsed objects should have a save attached")

    def update_object(self):
        if self.object is None:
            ArkSaveLogger.error_log("This object has no ArkGameObject associated with it, cannot update object")
            return
        if self.binary is None:
            ArkSaveLogger.error_log("This object has no binary associated with it, cannot update object")
            return

        self.object = ArkGameObject(uuid=self.object.uuid, blueprint=self.object.blueprint, binary_reader=self.binary)
        self.__init_props__()

    def get_short_name(self):
        return self.object.get_short_name() if self.object is not None else None