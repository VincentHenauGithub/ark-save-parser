from typing import Dict, Union, List
from uuid import UUID

from arkparse.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration, ArkBinaryParser
from arkparse.ftp.ark_ftp_client import ArkFtpClient
from arkparse.utils import TEMP_FILES_DIR

from arkparse.object_model import ArkGameObject
from arkparse.object_model.misc.object_owner import ObjectOwner
from arkparse.object_model.structures import Structure, StructureWithInventory
from arkparse.parsing.struct.actor_transform import MapCoords
from arkparse.enums.ark_map import ArkMap

class StructureApi:
    def __init__(self, save: AsaSave):
        self.save = save
        self.retrieved_all = False
        self.parsed_structures = {}

    def get_all_objects(self, config: GameObjectReaderConfiguration = None) -> Dict[UUID, ArkGameObject]:
        if config is None:
            reader_config = GameObjectReaderConfiguration(
                blueprint_name_filter=lambda name: name is not None and "/Structures" in name and not "PrimalItemStructure_" in name
            )
        else:
            reader_config = config

        objects = self.save.get_game_objects(reader_config)

        # for key, obj in objects.items():
        #     print(obj.blueprint)

        return objects
    
    def _parse_single_structure(self, obj: ArkGameObject) -> Union[Structure, StructureWithInventory]:
        if obj.uuid in self.parsed_structures.keys():
            return self.parsed_structures[obj.uuid]
        
        if obj.get_property_value("MaxItemCount") is not None or (obj.get_property_value("MyInventoryComponent") is not None and obj.get_property_value("CurrentItemCount") is not None):
            structure = StructureWithInventory(obj.uuid, self.save)
        else:
            structure = Structure(obj.uuid, self.save)

        for key, loc in self.save.save_context.actor_transforms.items():
            if key == obj.uuid:
                structure.set_actor_transform(loc)

        self.parsed_structures[obj.uuid] = structure

        return structure

    def get_all(self, config: GameObjectReaderConfiguration = None) -> Dict[UUID, Union[Structure, StructureWithInventory]]:

        if self.retrieved_all:
            return self.parsed_structures
        
        objects = self.get_all_objects(config)

        structures = {}

        for key, obj in objects.items():
            obj : ArkGameObject = obj
            if obj is None:
                print(f"Object is None for {key}")
                continue
            
            structure = self._parse_single_structure(obj)

            structures[obj.uuid] = structure

        if config is None:
            self.retrieved_all = True

        return structures
    
    def get_by_id(self, id: UUID) -> Union[Structure, StructureWithInventory]:
        obj = self.save.get_game_object_by_id(id)
        return self._parse_single_structure(obj)
    
    def get_at_location(self, map: ArkMap, coords: MapCoords, radius: float = 0.3, classes: List[str] = None) -> Dict[UUID, Union[Structure, StructureWithInventory]]:
        if classes is not None:
            config = GameObjectReaderConfiguration(
                blueprint_name_filter=lambda name: name in classes
            )
        else:
            config = None

        structures = self.get_all(config)
        result = {}

        for key, obj in structures.items():
            obj: Structure = obj
            if obj.location is None:
                continue

            if obj.location.is_at_map_coordinate(map, coords, tolerance=radius):
                result[key] = obj

        return result
    
    def remove_at_location(self, map: ArkMap, coords: MapCoords, radius: float = 0.3, owner_tribe_id: int = None):
        structures = self.get_at_location(map, coords, radius)

        for _, obj in structures.items():
            if owner_tribe_id is None or obj.owner.tribe_id == owner_tribe_id:
                obj.remove_from_save(self.save)
    
    def get_owned_by(self, owner: ObjectOwner = None, owner_tribe_id: int = None) -> Dict[UUID, Union[Structure, StructureWithInventory]]:
        result = {}
        
        if owner is None and owner_tribe_id is None:
            raise ValueError("Either owner or owner_tribe_id must be provided")

        structures = self.get_all()
        
        for key, obj in structures.items():
            if owner is not None and obj.is_owned_by(owner):
                result[key] = obj
            elif owner_tribe_id is not None and obj.owner.tribe_id == owner_tribe_id:
                result[key] = obj

        return result
    
    def get_by_class(self, blueprints: List[str]) -> Dict[UUID, Union[Structure, StructureWithInventory]]:
        result = {}

        config = GameObjectReaderConfiguration(
            blueprint_name_filter=lambda name: name in blueprints
        )

        structures = self.get_all(config)

        for key, obj in structures.items():
            result[key] = obj

        return result
    
    def filter_by_owner(self, structures: Dict[UUID, Union[Structure, StructureWithInventory]], owner: ObjectOwner = None, owner_tribe_id: int = None, invert: bool = False) -> Dict[UUID, Union[Structure, StructureWithInventory]]:
        result = {}

        if owner is None and owner_tribe_id is None:
            raise ValueError("Either owner or owner_tribe_id must be provided")

        for key, obj in structures.items():
            if owner is not None and obj.is_owned_by(owner) and not invert:
                result[key] = obj
            elif owner_tribe_id is not None and obj.owner.tribe_id == owner_tribe_id and not invert:
                result[key] = obj
            elif invert:
                result[key] = obj

        return result
    
    def filter_by_location(self, map: ArkMap, coords: MapCoords, radius: float, structures: Dict[UUID, Union[Structure, StructureWithInventory]]) -> Dict[UUID, Union[Structure, StructureWithInventory]]:
        result = {}

        for key, obj in structures.items():
            if obj.location.is_at_map_coordinate(map, coords, tolerance=radius):
                result[key] = obj

        return result
    
    def get_connected_structures(self, structures: Dict[UUID, Union[Structure, StructureWithInventory]]) -> Dict[UUID, Union[Structure, StructureWithInventory]]:
        result = structures.copy()
        new_found = True

        while new_found:
            new_found = False
            new_result = result.copy()
            for key, s in result.items():
                for uuid in s.linked_structure_uuids:
                    if uuid not in new_result.keys():
                        new_found = True
                        obj = self.get_by_id(uuid)
                        new_result[uuid] = obj
            result = new_result

        return result
     
    def modify_structures(self, structures: Dict[UUID, Union[Structure, StructureWithInventory]], new_owner: ObjectOwner = None, new_max_health: float = None, ftp_client: ArkFtpClient = None):
        for key, obj in structures.items():
            for uuid in obj.linked_structure_uuids:
                if uuid not in structures.keys():
                    raise ValueError(f"Linked structure {uuid} is not in the structures list, please change owner of all linked structures")

            if new_max_health is not None:
                obj.set_max_health(new_max_health)
            
            if new_owner is not None:
                obj.owner.replace_self_with(new_owner, binary=obj.binary)

            obj.update_binary()

        if ftp_client is not None:
            self.save.store_db(TEMP_FILES_DIR / "sapi_temp_save.ark")
            ftp_client.connect()
            ftp_client.upload_save_file(TEMP_FILES_DIR / "sapi_temp_save.ark")
            ftp_client.close()

    def create_heatmap(self, map: ArkMap, resolution: int = 100, structures: Dict[UUID, Union[Structure, StructureWithInventory]] = None, classes: List[str] = None, owner: ObjectOwner = None, min_in_section: int = 1):
        import math
        import numpy as np

        structs = structures

        if classes is not None:
            structs = self.get_by_class(classes)
        elif structures is None:
            structs = self.get_all()
        heatmap = [[0 for _ in range(resolution)] for _ in range(resolution)]

        for key, obj in structs.items():
            obj: Structure = obj
            if obj.location is None:
                continue

            if owner is not None and not obj.is_owned_by(owner):
                continue

            coords: MapCoords = obj.location.as_map_coords(map)
            y = math.floor(coords.long)
            x = math.floor(coords.lat)
            heatmap[x][y] += 1

        for i in range(resolution):
            for j in range(resolution):
                if heatmap[i][j] < min_in_section:
                    heatmap[i][j] = 0

        return np.array(heatmap)
    
    def get_all_with_inventory(self) -> Dict[UUID, StructureWithInventory]:
        structures = self.get_all()
        result = {}

        for key, obj in structures.items():
            if isinstance(obj, StructureWithInventory):
                result[key] = obj

        return result
    
    def get_container_of_inventory(self, inv_uuid: UUID, structures: dict[UUID, StructureWithInventory] = None) -> StructureWithInventory:
        if structures is None:
            structures = self.get_all_with_inventory()
        for _, obj in structures.items():
            if not isinstance(obj, StructureWithInventory):
                continue
            obj: StructureWithInventory = obj
            if obj.inventory_uuid == inv_uuid:
                return obj
        
        return None

    # def get_building_arround(self, key_piece: UUID) -> Dict[UUID, ArkGameObject]:
    #     result = {}
    #     new_found = True
    #     current = start

    #     while new_found:
    #         new_found = False
    #         result[current] = objects[current]
    #         for uuid in objects[current].linked_structure_uuids:
    #             if uuid not in result.keys():
    #                 new_found = True
    #                 current = uuid
    #                 break

    #     return result
