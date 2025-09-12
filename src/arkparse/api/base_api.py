from typing import Dict, List, Optional
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
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.utils import ImportFile
from arkparse.logging import ArkSaveLogger

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
    
    def get_base_at(self, coords: MapCoords, radius: float = 0.3, owner_tribe_id = None, keystone: Structure = None, owner_tribe_name = None) -> Base:
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

        if owner_tribe_id is not None or owner_tribe_name is not None:
            all_structures = {k: v for k, v in all_structures.items() if (v.owner.tribe_id == owner_tribe_id or v.owner.tribe_name == owner_tribe_name)}

        if keystone is None:
            keystone = self.__get_closest_to(all_structures, coords)
        keystone_owner = keystone.owner if keystone is not None else None
        filtered_structures = {k: v for k, v in all_structures.items() if v.owner == keystone_owner}

        return Base(keystone.object.uuid, filtered_structures) if keystone is not None else None
    
    def __get_all_files_from_dir_recursive(self, dir_path: Path) -> tuple[list[ImportFile], Optional[Path]]:
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

        files: Optional[List[ImportFile]] = None
        base_file: Optional[Path] = None
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
    
    def get_all_bases(self, only_connected: bool = False, radius: float = 0.3) -> List[Base]:
        all_bases: List[Base] = []
        all_structures: Dict[UUID, Structure] = super().get_all()
        visited_structures: List[UUID] = []

        for key, structure in all_structures.items():
            base = None
            if key in visited_structures:
                continue
    
            if only_connected:
                connected = self.get_connected_structures({key: structure})
                base = Base(structure.uuid, connected)
                all_bases.append(base)
            else:
                base = self.get_base_at(structure.location.as_map_coords(self.map), radius, structure.owner.tribe_id, structure)

            for structure in base.structures.values():
                visited_structures.append(structure.uuid)

            ArkSaveLogger.api_log(f"Parsed base at {'Unknown' if base.location is None else base.keystone.location.as_map_coords(self.map)} with {len(base.structures)} structures, owner: {base.owner}")

        return all_bases

                

        

    

        
