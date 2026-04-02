from typing import Dict, Union, List, Tuple
from uuid import UUID
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

from arkparse.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.object_model.misc.object_owner import ObjectOwner
from arkparse.object_model.structures import Structure, StructureWithInventory
from arkparse.parsing.struct.actor_transform import MapCoords
from arkparse.enums.ark_map import ArkMap
from arkparse.logging import ArkSaveLogger
from arkparse.logging.ark_save_logger import mark_as_worker_thread


def _is_parallel_enabled() -> bool:
    if hasattr(sys, '_is_gil_enabled'):
        return not sys._is_gil_enabled()
    return False


_PARALLEL_ENABLED = _is_parallel_enabled()

SKIPPED_STRUCTURE_BPS = []

class StructureApi:
    def __init__(self, save: AsaSave):
        self.save = save
        self.retrieved_all = False
        self.parsed_structures = {}

    def get_all_objects(self, config: GameObjectReaderConfiguration = None) -> Dict[UUID, ArkGameObject]:
        if config is None:
            ArkSaveLogger.api_log("Retrieving all structure objects from save")
            reader_config = GameObjectReaderConfiguration(
                blueprint_name_filter=lambda name: name is not None \
                                                   and "Structures" in name \
                                                   and (not "PrimalItemStructure_" in name or "PrimalItemStructure_ASR" in name) \
                                                   and not "/Skins/" in name \
                                                   and not "PrimalInventory" in name \
                                                   and not "/TreasureMap/" in name \
                                                #    and not "Tileset" in name \
                                                   and not "PrimalItemStructureSkin" in name \
                                                   and not "PrimalItemResource" in name \
                                                   and not "/TrainCarts/" in name \
            )

            objects = self.save.get_game_objects(reader_config)

            ArkSaveLogger.api_log(f"Found {len(objects)} structure objects, now looking for containers that were missed")
            config = GameObjectReaderConfiguration()
            config.property_names = ["MyInventoryComponent"]
            config.blueprint_name_filter = lambda name: name is not None and not "PlayerPawn" in name and not "/Dinos/" in name and not "Character_BP" in name
            containers = self.save.get_game_objects(config)
            for key, obj in containers.items():
                if key not in objects.keys():
                    objects[key] = obj
            ArkSaveLogger.api_log(f"After adding containers, {len(objects)} structure objects remain")

            # Filter engrams out
            ArkSaveLogger.api_log("Filtering engrams out of structure list")
            for key in list(objects.keys()):
                obj: ArkGameObject = objects[key]
                if obj.get_property_value("bIsEngram") is not None:
                    del objects[key]

            ArkSaveLogger.api_log(f"After filtering engrams, {len(objects)} structure objects remain")
        else:
            reader_config = config
            objects = self.save.get_game_objects(reader_config)

        ArkSaveLogger.api_log(f"Total objects retrieved for structure parsing: {len(objects)}")
        to_remove = []
        for obj in objects.values():
            if obj.get_property_value("StructureID") is None:
                if obj.blueprint not in SKIPPED_STRUCTURE_BPS:
                    SKIPPED_STRUCTURE_BPS.append(obj.blueprint)
                    ArkSaveLogger.warning_log(f"Object {obj.uuid} ({obj.blueprint}) does not seem to be a structure, skipping bps of this type")
                to_remove.append(obj.uuid)

        for uuid in to_remove:
            del objects[uuid]
            
        ArkSaveLogger.api_log(f"Total structure objects after filtering non-structures: {len(objects)}")

        return objects

    def _parse_single_structure(self, obj: ArkGameObject, bypass_inventory: bool = True) -> Union[Structure, StructureWithInventory]:
        if obj.uuid in self.parsed_structures.keys():
            return self.parsed_structures[obj.uuid]
        
        try:
            if obj.get_property_value("MyInventoryComponent") is not None:
                structure = StructureWithInventory(obj.uuid, self.save, bypass_inventory=bypass_inventory)
            else:
                structure = Structure(obj.uuid, self.save)

            if structure is None:
                return None

            if obj.uuid in self.save.save_context.actor_transforms:
                structure.set_actor_transform(self.save.save_context.actor_transforms[obj.uuid])

            self.parsed_structures[obj.uuid] = structure
        except Exception as e:
            if ArkSaveLogger._allow_invalid_objects:
                ArkSaveLogger.error_log(f"Failed to parse structure {obj.uuid}: {e}")
            else:
                raise e

        return structure

    def _parse_structures_batch(self, to_parse: List[Tuple[UUID, ArkGameObject]], structures: Dict, bypass_inventory: bool, max_workers: int):
        if _PARALLEL_ENABLED and max_workers > 1 and len(to_parse) > 0:
            ArkSaveLogger.api_log(f"Parsing {len(to_parse)} structures with {max_workers} workers...")
            save = self.save
            actor_transforms = self.save.save_context.actor_transforms
            _worker_initialized = threading.local()
            error_count = [0]

            def parse_single(item):
                if not getattr(_worker_initialized, 'done', False):
                    mark_as_worker_thread()
                    _worker_initialized.done = True
                key, obj = item
                try:
                    if obj.get_property_value("MyInventoryComponent") is not None:
                        s = StructureWithInventory(obj.uuid, save, bypass_inventory=bypass_inventory)
                    else:
                        s = Structure(obj.uuid, save)
                    if s is not None and obj.uuid in actor_transforms:
                        s.set_actor_transform(actor_transforms[obj.uuid])
                    return (key, obj.uuid, s, None)
                except Exception as e:
                    error_count[0] += 1
                    if error_count[0] <= 3:
                        ArkSaveLogger.error_log(f"Parallel structure parse error #{error_count[0]}: {type(e).__name__}: {e}")
                    return (key, obj.uuid, None, str(e))

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(executor.map(parse_single, to_parse))

            for key, uuid, structure, error in results:
                if structure is not None:
                    structures[uuid] = structure
                    self.parsed_structures[uuid] = structure
                elif error is not None:
                    if not ArkSaveLogger._allow_invalid_objects:
                        raise RuntimeError(f"Structure parse error for {uuid}: {error}")
        else:
            for key, obj in to_parse:
                structure = self._parse_single_structure(obj, bypass_inventory)
                if structure is not None:
                    structures[obj.uuid] = structure

    def get_all(self, config: GameObjectReaderConfiguration = None, bypass_inventory: bool = True, max_workers: int = 6) -> Dict[UUID, Union[Structure, StructureWithInventory]]:

        if self.retrieved_all and config is None:
            return self.parsed_structures
        
        objects = self.get_all_objects(config)

        structures = {}

        # Classify: cached vs to-parse
        to_parse: List[Tuple[UUID, ArkGameObject]] = []
        for key, obj in objects.items():
            if obj is None:
                print(f"Object is None for {key}")
                continue
            if obj.uuid in self.parsed_structures:
                structures[obj.uuid] = self.parsed_structures[obj.uuid]
            else:
                to_parse.append((key, obj))

        ArkSaveLogger.api_log(f"Parsing {len(to_parse)} structure objects ({len(structures)} cached)")

        # Pre-cache UUID→class mappings to avoid SQLite lock contention during parallel inventory parsing
        if not bypass_inventory and max_workers > 1 and _PARALLEL_ENABLED and len(to_parse) > 0:
            self.save.save_connection.cache_all_classes()

        self._parse_structures_batch(to_parse, structures, bypass_inventory, max_workers)

        if config is None:
            self.retrieved_all = True

        return structures

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

        ArkSaveLogger.api_log(f"Getting structures at location {coords} on map {map.name} within radius {radius}")

        for key, obj in structures.items():
            obj: Structure = obj
            if obj.location is None:
                continue
            
            if obj.location.is_at_map_coordinate(map, coords, tolerance=radius):
                result[key] = obj

        return result
    
    def remove_at_location(self, map: ArkMap, coords: MapCoords, radius: float = 0.3, owner_tribe_id: int = None, owner_tribe_name: str = None):
        structures = self.get_at_location(map, coords, radius)
        
        removed = []
        for uuid, obj in structures.items():
            if (owner_tribe_id is None and owner_tribe_name is None) or obj.owner.tribe_id == owner_tribe_id or obj.owner.tribe_name == owner_tribe_name:
                self.save.remove_obj_from_db(uuid)
                removed.append(uuid)
                self.parsed_structures.pop(uuid, None)

        ArkSaveLogger.api_log(f"Removed {len(removed)} structures at location {coords} on map {map.name}")

        return removed

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
        processed = []

        while new_found:
            new_found = False
            new_result = result.copy()
            unprocessed = [s for s in result.values() if s.uuid not in processed]
            for s in unprocessed:
                if s.uuid in processed:
                    continue
                for uuid in s.linked_structure_uuids:
                    if uuid not in new_result.keys() and uuid not in ignore and uuid not in processed:
                        new_found = True
                        obj = self.get_by_id(uuid)
                        if obj is not None:
                            new_result[uuid] = obj
                        else:
                            ignore.append(uuid)
                            ArkSaveLogger.api_log(f"Could not find linked structure {uuid}, ignoring")
                    processed.append(s.uuid)
            result = new_result

            # ArkSaveLogger.api_log(f"Connected structures found so far: {len(result)}")

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
        result = {key: obj for key, obj in structures.items() if isinstance(obj, StructureWithInventory)}

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
