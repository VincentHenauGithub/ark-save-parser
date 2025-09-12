from typing import Dict, Union, List
from uuid import UUID

from arkparse.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.object_model.misc.object_owner import ObjectOwner
from arkparse.object_model.structures import Structure, StructureWithInventory
from arkparse.parsing.struct.actor_transform import MapCoords
from arkparse.enums.ark_map import ArkMap
from arkparse.logging import ArkSaveLogger

class StructureApi:
    def __init__(self, save: AsaSave):
        self.save = save
        self.retrieved_all = False
        self.parsed_structures = {}

    def get_all_objects(self, config: GameObjectReaderConfiguration = None) -> Dict[UUID, ArkGameObject]:
        if config is None:
            reader_config = GameObjectReaderConfiguration(
                blueprint_name_filter=lambda name: name is not None \
                                                   and "/Structures" in name \
                                                   and not "PrimalItemStructure_" in name \
                                                   and not "/Skins/" in name \
                                                   and not "PrimalInventory" in name \
                                                   and not "/TreasureMap/" in name \
                                                #    and not "Tileset" in name \
                                                   and not "PrimalItemStructureSkin" in name
                                                   and not "PrimalItemResource" in name \
                                                   and not "/TrainCarts/" in name \
            )
        else:
            reader_config = config

        objects = self.save.get_game_objects(reader_config)

        return objects

    def _parse_single_structure(self, obj: ArkGameObject, bypass_inventory: bool = True) -> Union[Structure, StructureWithInventory]:
        if obj.uuid in self.parsed_structures.keys():
            return self.parsed_structures[obj.uuid]
        
        try:
            if obj.get_property_value("MaxItemCount") is not None or (obj.get_property_value("MyInventoryComponent") is not None and obj.get_property_value("CurrentItemCount") is not None):
                structure = StructureWithInventory(obj.uuid, self.save, bypass_inventory=bypass_inventory)
            else:
                structure = Structure(obj.uuid, self.save)

            if obj.uuid in self.save.save_context.actor_transforms:
                structure.set_actor_transform(self.save.save_context.actor_transforms[obj.uuid])

            self.parsed_structures[obj.uuid] = structure
        except Exception as e:
            if ArkSaveLogger._allow_invalid_objects:
                ArkSaveLogger.error_log(f"Failed to parse structure {obj.uuid}: {e}")
            else:
                raise e

        return structure

    def get_all(self, config: GameObjectReaderConfiguration = None, bypass_inventory: bool = True) -> Dict[UUID, Union[Structure, StructureWithInventory]]:

        if self.retrieved_all and config is None:
            return self.parsed_structures
        
        objects = self.get_all_objects(config)

        structures = {}

        for key, obj in objects.items():
            obj : ArkGameObject = obj
            if obj is None:
                print(f"Object is None for {key}")
                continue

            if obj.get_property_value("StructureID") is None:
                ArkSaveLogger.warning_log(f"Object {obj.uuid} ({obj.blueprint}) does not seem to be a structure, skipping")
                continue
            
            structure = self._parse_single_structure(obj, bypass_inventory)

            structures[obj.uuid] = structure

        if config is None:
            self.retrieved_all = True

        return structures    

    def get_by_id(self, id: UUID) -> Union[Structure, StructureWithInventory]:
        obj = self.save.get_game_object_by_id(id)
        if obj is None:
            return None
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
    
    def remove_at_location(self, map: ArkMap, coords: MapCoords, radius: float = 0.3, owner_tribe_id: int = None, owner_tribe_name: str = None):
        structures = self.get_at_location(map, coords, radius)

        for _, obj in structures.items():
            if owner_tribe_id is None or obj.owner.tribe_id == owner_tribe_id or obj.owner.tribe_name == owner_tribe_name:
                obj.remove_from_save(self.save)

    def get_owned_by(self, owner: ObjectOwner = None, owner_tribe_id: int = None, owner_tribe_name: str = None) -> Dict[UUID, Union[Structure, StructureWithInventory]]:
        result = {}

        if owner is None and owner_tribe_id is None and owner_tribe_name is None:
            raise ValueError("Either owner, owner_tribe_id or owner_tribe_name must be provided")

        structures = self.get_all()
        
        for key, obj in structures.items():
            if owner is not None and obj.is_owned_by(owner):
                result[key] = obj
            elif owner_tribe_id is not None and obj.owner.tribe_id == owner_tribe_id:
                result[key] = obj
            elif owner_tribe_name is not None and obj.owner.tribe_name == owner_tribe_name:
                result[key] = obj

        return result
    
    def get_by_class(self, blueprints: List[str]) -> Dict[UUID, Union[Structure, StructureWithInventory]]:
        result = {}

        config = GameObjectReaderConfiguration(
            blueprint_name_filter=lambda name: name in blueprints
        )

        ArkSaveLogger.api_log(f"Getting structures by class filter: {blueprints}")

        structures = self.get_all(config)

        for key, obj in structures.items():
            result[key] = obj

        # for key, obj in structures.items():
        #     print(obj.blueprint)

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
        ignore = []

        while new_found:
            new_found = False
            new_result = result.copy()
            for _, s in result.items():
                for uuid in s.linked_structure_uuids:
                    if uuid not in new_result.keys() and uuid not in ignore:
                        new_found = True
                        obj = self.get_by_id(uuid)
                        if obj is not None:
                            new_result[uuid] = obj
                        else:
                            ignore.append(uuid)
                            ArkSaveLogger.api_log(f"Could not find linked structure {uuid}, ignoring")
            result = new_result

        return result
     
    def modify_structures(self, structures: Dict[UUID, Union[Structure, StructureWithInventory]], new_owner: ObjectOwner = None, new_max_health: float = None):
        for key, obj in structures.items():
            for uuid in obj.linked_structure_uuids:
                if uuid not in structures.keys():
                    raise ValueError(f"Linked structure {uuid} is not in the structures list, please change owner of all linked structures")

            if new_max_health is not None:
                obj.set_max_health(new_max_health)
            
            if new_owner is not None:
                obj.owner.replace_self_with(new_owner, binary=obj.binary)

            obj.update_binary()

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
