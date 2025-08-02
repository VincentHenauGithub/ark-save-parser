from ..ark_game_object import ArkGameObject
from uuid import UUID, uuid4
import json
from arkparse.parsing import ArkBinaryParser
from pathlib import Path
from arkparse.logging import ArkSaveLogger
from importlib.resources import files
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from arkparse import AsaSave

class ParsedObjectBase:
    binary: ArkBinaryParser = None
    object: ArkGameObject = None
    props_initialized: bool = False
    save: "AsaSave" = None

    def __get_class_name(self):
        self.binary.set_position(0)
        self.binary.read_name()

    def __init_props__(self):
        pass

    def __init__(self, uuid: UUID = None, save: "AsaSave" = None):
        if uuid is None or save is None:
            return
        if save is not None:
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

    def store_binary(self, path: Path, name: str = None, prefix: str = "obj_", no_suffix= False):
        name = name if name is not None else str(self.object.uuid)
        file_path = path / (f"{prefix}{name}.bin" if not no_suffix else f"{prefix}{name}")
        name_path = path / (f"{prefix}{name}_n.json")

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

    def get_short_name(self):
        to_strip_end = [
            "_C",
        ]

        to_strip_start = [
            "PrimalItemResource_",
            "PrimalItemAmmo_",
        ]

        short = self.object.blueprint.split('/')[-1].split('.')[0]

        for strip in to_strip_end:
            if short.endswith(strip):
                short = short[:-len(strip)]

        for strip in to_strip_start:
            if short.startswith(strip):
                short = short[len(strip):]

        return short