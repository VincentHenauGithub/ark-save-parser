from typing import Dict, List
from uuid import UUID, uuid4
from pathlib import Path
import os
import json

from arkparse.api.structure_api import StructureApi
from arkparse.parsing.struct.actor_transform import MapCoords
from arkparse.object_model.structures import Structure, StructureWithInventory
from arkparse.object_model.bases.base import Base
from arkparse.object_model.misc.inventory import Inventory
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.enums import ArkMap
from arkparse.parsing.struct import ActorTransform
from arkparse.parsing import ArkBinaryParser
from arkparse.object_model import ArkGameObject


class ImportFile:
    def __init__(self, path: str):
        def read_bytes_from_file(file_path: Path) -> bytes:
            with open(file_path, "rb") as f:
                return f.read()
            
        file = path.split("\\")[-1]
        uuid = UUID(file.split("_")[1].split('.')[0])
        t = file.split("_")[0]
        name_path = None if t == "loc" else Path(path).parent / (file.split('.')[0] + "_n.json")

        self.path: Path = Path(path)
        self.type: str = t
        self.uuid: UUID = uuid
        self.names: Dict[int, str] = json.loads(name_path.read_text()) if name_path is not None else None
        self.bytes = read_bytes_from_file(path)

class BaseApi(StructureApi):
    def __init__(self, save, map: ArkMap):
        super().__init__(save)
        self.map = map

    def __get_closest_to(self, structures: Dict[UUID, Structure], coords: MapCoords):
        closest = None
        closest_dist = None

        for key, structure in structures.items():
            s_coords = structure.location.as_map_coords(self.map)
            dist = s_coords.distance_to(coords)
            if closest is None or dist < closest_dist:
                closest = structure
                closest_dist = dist

        return closest

    def get_base_at(self, coords: MapCoords, radius: float = 0.3, owner_tribe_id = None) -> Base:
        structures = self.get_at_location(self.map, coords, radius)
        if structures is None or len(structures) == 0:
            return None
        
        all_structures: Dict[UUID, Structure] = {}
        for key, structure in structures.items():
            all_structures[key] = structure
            connected = self.get_connected_structures(structures)
            for key, conn_structure in connected.items():
                if key not in all_structures:
                    all_structures[key] = conn_structure

        if owner_tribe_id is not None:
            all_structures = {k: v for k, v in all_structures.items() if v.owner.tribe_id == owner_tribe_id}

        keystone = self.__get_closest_to(all_structures, coords)

        keystone_owner = keystone.owner if keystone is not None else None

        filtered_structures = {k: v for k, v in all_structures.items() if v.owner == keystone_owner}

        return Base(keystone.object.uuid, filtered_structures)
    
    def __get_all_files_from_dir_recursive(self, dir_path: Path) -> Dict[str, bytes]:
        out = []
        base_file = None
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = Path(root) / Path(file)
                if file_path.name == "base.json":
                    base_file = file_path
                elif file_path.name.endswith(".bin") or file_path.name.startswith("loc_"):
                    out.append(ImportFile(str(file_path)))
        return out, base_file
    
    def import_base(self, path: Path, location: ActorTransform = None) -> Base:
        uuid_translation_map = {}
        # interconnection_properties = [
        #     "PlacedOnFloorStructure",
        #     "MyInventoryComponent",
        #     "WirelessSources",
        #     "WirelessConsumers",
        #     "InventoryItems",
        #     "OwnerInventory",
        #     "StructuresPlacedOnFloor",
        #     "LinkedStructures"
        # ]

        def replace_uuids(uuid_map: Dict[UUID, UUID], bytes_: bytes):
            for uuid in uuid_map:
                new_bytes = uuid_map[uuid].bytes            
                old_bytes = uuid.bytes
                bytes_ = bytes_.replace(old_bytes, new_bytes)
                # print(f"Replacing {uuid} with {uuid_map[uuid]}")
            return bytes_

        actor_transforms: Dict[UUID, ActorTransform] = {}
        structures: Dict[UUID, Structure] = {}

        files: List[ImportFile] = None
        base_file: Path = None
        files, base_file = self.__get_all_files_from_dir_recursive(path)

        # assign new uuids to all
        for file in files:
            uuid_translation_map[file.uuid] = uuid4()

        # Assign new uuids to all actor transforms and add them to the database
        new_actor_transforms: bytes = bytes()
        for file in files:
            if file.type == "loc":
                new_uuid: UUID = uuid_translation_map[file.uuid]
                actor_transforms[new_uuid] = ActorTransform(from_json=Path(file.path))
                new_actor_transforms += new_uuid.bytes + actor_transforms[new_uuid].to_bytes()
        self.save.add_actor_transforms(new_actor_transforms)
        # Update actor transforms in save context
        self.save.read_actor_locations()

        # get all inventory items and add them to DB
        for file in files:
            if file.type == "itm":
                new_uuid = uuid_translation_map[file.uuid]
                parser = ArkBinaryParser(file.bytes, self.save.save_context)
                parser.byte_buffer = replace_uuids(uuid_translation_map, parser.byte_buffer)
                parser.replace_name_ids(file.names, self.save)
                self.save.add_obj_to_db(new_uuid, parser.byte_buffer)
                item = InventoryItem(uuid=new_uuid, save=self.save)
                item.reidentify(new_uuid)
                
                # parser = ArkBinaryParser(self.save.get_game_obj_binary(new_uuid), self.save.save_context)
                # obj = ArkGameObject(uuid=new_uuid, binary_reader=parser)

        # Get all inventories and add them to DB
        for file in files:
            if file.type == "inv":
                new_uuid = uuid_translation_map[file.uuid]
                parser = ArkBinaryParser(file.bytes, self.save.save_context)
                parser.byte_buffer = replace_uuids(uuid_translation_map, parser.byte_buffer)
                parser.replace_name_ids(file.names, self.save)
                self.save.add_obj_to_db(new_uuid, parser.byte_buffer)
                inventory = Inventory(uuid=new_uuid, save=self.save)
                inventory.reidentify(new_uuid)
                
                # parser = ArkBinaryParser(self.save.get_game_obj_binary(new_uuid), self.save.save_context)
                # obj = ArkGameObject(uuid=new_uuid, binary_reader=parser)

        # Get all structures and add them to DB
        for file in files:
            if file.type == "str":
                new_uuid = uuid_translation_map[file.uuid]
                parser = ArkBinaryParser(file.bytes, self.save.save_context)
                parser.byte_buffer = replace_uuids(uuid_translation_map, parser.byte_buffer)
                parser.replace_name_ids(file.names, self.save)
                self.save.add_obj_to_db(new_uuid, parser.byte_buffer)
                obj = ArkGameObject(uuid=new_uuid, binary_reader=parser)
                structure = self._parse_single_structure(obj)
                structure.reidentify(new_uuid)
                if isinstance(structure, StructureWithInventory) and structure.inventory is not None:
                    structure.inventory.renumber_name(new_number=structure.object.get_name_number())
                    structure.inventory.update_binary()
                structures[new_uuid] = structure
                # parser = ArkBinaryParser(self.save.get_game_obj_binary(new_uuid), self.save.save_context)
                # obj = ArkGameObject(uuid=new_uuid, binary_reader=parser)

        keystone_uuid = uuid_translation_map[UUID(json.loads(Path(base_file).read_text())["keystone"])]
        base = Base(keystone_uuid, structures)
        # base = Base(structures=structures)

        # input(f"Imported base with {len(structures)} structures, keystone {base.keystone.object.uuid} at {base.keystone.location}")
        if location is not None:
            base.move_to(location, self.save)

        return base

                

        

    

        
