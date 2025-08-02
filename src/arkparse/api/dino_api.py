from typing import Dict, List
from uuid import UUID

from arkparse.object_model.cryopods.cryopod import Cryopod
from arkparse.object_model.dinos.dino import Dino
from arkparse.object_model.dinos.tamed_baby import TamedBaby
from arkparse.object_model.dinos.baby import Baby
from arkparse.object_model.dinos.tamed_dino import TamedDino
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.object_model.misc.dino_owner import DinoOwner
from arkparse.ftp.ark_ftp_client import ArkFtpClient

from arkparse.parsing import ArkBinaryParser
from arkparse.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.parsing.struct.actor_transform import MapCoords
from arkparse.enums import ArkMap, ArkStat
from arkparse.utils import TEMP_FILES_DIR
from arkparse.logging import ArkSaveLogger

class DinoApi:
    def __init__(self, save: AsaSave):
        self.save = save
        self.all_objects = None
        self.parsed_dinos: Dict[UUID, Dino] = {}
        self.parsed_cryopods: Dict[UUID, Cryopod] = {}

    def get_all_objects(self, config: GameObjectReaderConfiguration = None) -> Dict[UUID, ArkGameObject]:
        reuse = False

        if config is None:
            reuse = True
            if self.all_objects is not None:
                return self.all_objects

            config = GameObjectReaderConfiguration(
                blueprint_name_filter=lambda name: \
                    name is not None and \
                        (("Dinos/" in name and "_Character_" in name) or \
                        ("PrimalItem_WeaponEmptyCryopod_C" in name)))

        objects = self.save.get_game_objects(config)
        
        if reuse:
            self.all_objects = objects

        return objects
    
    def get_by_uuid(self, uuid: UUID) -> Dino:
        object = self.save.get_game_object_by_id(uuid)

        if object is None:
            return None
        
        dino = None
        if "Dinos/" in object.blueprint and "_Character_" in object.blueprint:
            is_tamed = object.get_property_value("TamedTimeStamp") is not None

            if uuid in self.parsed_dinos:
                dino = self.parsed_dinos[uuid]
            else:
                if is_tamed:
                    dino = TamedDino(uuid, self.save)
                else:
                    dino = Dino(uuid, self.save)
                self.parsed_dinos[uuid] = dino

        return dino

    def get_all(self, config = None, include_cryos: bool = True, include_wild: bool = True, include_tamed: bool = True, include_babies: bool = True) -> Dict[UUID, Dino]:
        ArkSaveLogger.api_log("Retrieving all dinos from save...")

        objects = self.get_all_objects(config)
        dinos = {}

        ArkSaveLogger.api_log(f"Found {len(objects)} dinos, parsing them... (and retrieving inventories)")
        for key, obj in objects.items():
            dino = None
            if "Dinos/" in obj.blueprint and "_Character_" in obj.blueprint:
                is_tamed = obj.get_property_value("TamedTimeStamp") is not None
                is_baby = obj.get_property_value("bIsBaby", False)

                if obj.uuid in self.parsed_dinos:
                    if is_tamed and include_tamed:
                        if is_baby and include_babies:
                            dino = self.parsed_dinos[obj.uuid]
                        else:
                            dino = self.parsed_dinos[obj.uuid]
                    elif not is_tamed and include_wild:
                        if is_baby and include_babies:
                            dino = self.parsed_dinos[obj.uuid]
                        else:
                            dino = self.parsed_dinos[obj.uuid]
                elif is_tamed and include_tamed:
                    if is_baby and include_babies:
                        dino = TamedBaby(obj.uuid, save=self.save)
                    else:
                        dino = TamedDino(obj.uuid, save=self.save)
                    self.parsed_dinos[obj.uuid] = dino
                elif include_wild and not is_tamed:
                    if is_baby and include_babies:
                        dino = Baby(obj.uuid, save=self.save)
                    else:
                        dino = Dino(obj.uuid, save=self.save)
                    self.parsed_dinos[obj.uuid] = dino

            elif "PrimalItem_WeaponEmptyCryopod_C" in obj.blueprint and include_cryos and include_tamed:
                if not obj.get_property_value("bIsEngram", default=False):
                    if obj.uuid in self.parsed_cryopods:
                        is_baby = self.parsed_cryopods[obj.uuid].dino is not None and isinstance(self.parsed_cryopods[obj.uuid].dino, TamedBaby)
                        if is_baby and include_babies:
                            dino = self.parsed_cryopods[obj.uuid].dino
                        else:
                            dino = self.parsed_cryopods[obj.uuid].dino
                    else:
                        try:
                            cryopod = Cryopod(obj.uuid, save=self.save)
                            self.parsed_cryopods[obj.uuid] = cryopod
                            if cryopod.dino is not None:
                                dino = cryopod.dino
                                dino.is_cryopodded = True
                        except Exception as e:
                            if "Unsupported embedded data version" in str(e):
                                ArkSaveLogger.warning_log(f"Skipping cryopod {obj.uuid} due to unsupported embedded data version (pre Unreal 5.5)")
                                continue
                            ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.PARSER, True)
                            parser = ArkBinaryParser(self.save.get_game_obj_binary(obj.uuid), self.save.save_context)
                            cryopod = Cryopod(obj.uuid, parser)
                            ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.PARSER, False)
                            ArkSaveLogger.error_log(f"Error parsing cryopod {obj.uuid}: {e}")

                            if ArkSaveLogger._allow_invalid_objects:
                                continue
                            raise e
            
            if dino is not None:
                dinos[key] = dino

        ArkSaveLogger.api_log(f"Parsed {len(dinos)} dinos")

        return dinos
    
    def get_at_location(self, map: ArkMap, coords: MapCoords, radius: float = 0.3, tamed: bool = True, untamed: bool = True) -> Dict[UUID, Dino]:
        dinos = self.get_all()

        filtered_dinos = {}

        for key, dino in dinos.items():
            if isinstance(dino, TamedDino) and dino.cryopod is not None:
                continue

            if dino.location.is_at_map_coordinate(map, coords, tolerance=radius):
                if (tamed and isinstance(dino, TamedDino)) or (untamed and not isinstance(dino, TamedDino)):
                    filtered_dinos[key] = dino

        return filtered_dinos
    
    def get_all_wild(self) -> Dict[UUID, Dino]:
        return self.get_all(include_cryos=False, include_tamed=False)
    
    def get_all_tamed(self, include_cryopodded = True) -> Dict[UUID, TamedDino]:
        return self.get_all(include_cryos=include_cryopodded, include_wild=False, include_tamed=True)

    def get_all_babies(self, include_tamed: bool = True, include_cryopodded: bool = True, include_wild: bool = False) -> Dict[UUID, TamedBaby]:
        dinos = self.get_all(include_cryos=include_cryopodded, include_wild=include_wild, include_tamed=include_tamed)

        babies = {key: dino for key, dino in dinos.items() if isinstance(dino, Baby)}

        return babies
    
    def get_all_in_cryopod(self) -> Dict[UUID, TamedDino]:
        return self.get_all(include_cryos=True, include_wild=False, include_tamed=False)
    
    def get_all_by_class(self, class_names: List[str]) -> Dict[UUID, Dino]:
        config = GameObjectReaderConfiguration(
            blueprint_name_filter=lambda name: name is not None and name in class_names
        )

        dinos = self.get_all(config)
        class_dinos = {k: v for k, v in dinos.items() if v.object.blueprint in class_names}

        return class_dinos
    
    def get_all_wild_by_class(self, class_name: List[str]) -> Dict[UUID, Dino]:
        dinos = self.get_all_by_class(class_name)
        wild_dinos = {k: v for k, v in dinos.items() if not isinstance(v, TamedDino)}

        return wild_dinos
    
    def get_all_tamed_by_class(self, class_name: List[str]) -> Dict[UUID, TamedDino]:
        dinos = self.get_all_by_class(class_name)
        tamed_dinos = {k: v for k, v in dinos.items() if isinstance(v, TamedDino)}

        return tamed_dinos
    
    def get_all_of_at_least_level(self, level: int) -> Dict[UUID, Dino]:
        dinos = self.get_all()
        level_dinos = {k: v for k, v in dinos.items() if v.stats.current_level >= level}

        return level_dinos
    
    def get_all_wild_of_at_least_level(self, level: int) -> Dict[UUID, Dino]:
        dinos = self.get_all_of_at_least_level(level)
        wild_dinos = {k: v for k, v in dinos.items() if not isinstance(v, TamedDino)}

        return wild_dinos
    
    def get_all_tamed_of_at_least_level(self, level: int) -> Dict[UUID, TamedDino]:
        dinos = self.get_all_of_at_least_level(level)
        tamed_dinos = {k: v for k, v in dinos.items() if isinstance(v, TamedDino)}

        return tamed_dinos
    
    def get_all_with_stat_of_at_least(self, value: int, stat: List[ArkStat] = None) -> Dict[UUID, Dino]:
        dinos = self.get_all()
        filtered_dinos = {}
        
        for key, dino in dinos.items():
            stats_above = dino.stats.get_of_at_least(value)
            if len(stats_above) and (stat is None or any(s in stats_above for s in stat)):
                filtered_dinos[key] = dinos[key]

        return filtered_dinos
    
    def get_all_filtered(self, level_lower_bound: int = None, level_upper_bound: int = None, 
                         class_names: List[str] = None, 
                         tamed: bool = None, 
                         include_cryopodded: bool = True, only_cryopodded: bool = False, 
                         stat_minimum: int = None, stats: List[ArkStat] = None) -> Dict[UUID, Dino]:
        dinos = None

        if class_names is not None:
            config = GameObjectReaderConfiguration(
                blueprint_name_filter=lambda name: name is not None and name in class_names
            )
            ArkSaveLogger.api_log(f"Getting all dinos with specified class names")
            dinos = self.get_all(config)

            # get cryopodded dinos
            if include_cryopodded:
                ArkSaveLogger.api_log(f"Also getting cryopodded dinos with specified class names")
                cryopod_dinos = self.get_all_in_cryopod()
                for key, dino in cryopod_dinos.items():
                    if dino.object.blueprint in class_names:
                        dinos[key] = dino
        else:
            ArkSaveLogger.api_log("No class names provided, getting all dinos.")
            dinos = self.get_all()

        filtered_dinos = dinos

        ArkSaveLogger.api_log(f"Filtering {len(filtered_dinos)} dinos with the following criteria:")
        if level_lower_bound is not None:
            filtered_dinos = {k: v for k, v in filtered_dinos.items() if v.stats.current_level >= level_lower_bound}
            ArkSaveLogger.api_log(f"LowerLvBound - Filtered to {len(filtered_dinos)} dinos")
        
        if level_upper_bound is not None:
            filtered_dinos = {k: v for k, v in filtered_dinos.items() if v.stats.current_level <= level_upper_bound}
            ArkSaveLogger.api_log(f"UpperLvBound - Filtered to {len(filtered_dinos)} dinos")

        if class_names is not None:
            filtered_dinos = {k: v for k, v in filtered_dinos.items() if v.object.blueprint in class_names}
            ArkSaveLogger.api_log(f"Class - Filtered to {len(filtered_dinos)} dinos")

        if tamed is not None:
            if tamed:
                filtered_dinos = {k: v for k, v in filtered_dinos.items() if isinstance(v, TamedDino)}
                ArkSaveLogger.api_log(f"Tamed - Filtered to {len(filtered_dinos)} dinos")
            else:
                filtered_dinos = {k: v for k, v in filtered_dinos.items() if not isinstance(v, TamedDino)}
                ArkSaveLogger.api_log(f"Untamed - Filtered to {len(filtered_dinos)} dinos")

        if not include_cryopodded:
            filtered_dinos = {k: v for k, v in filtered_dinos.items() if not(isinstance(v, TamedDino) and v.cryopod is not None)}
            ArkSaveLogger.api_log(f"IncludeCryopodded - Filtered to {len(filtered_dinos)} dinos")

        if only_cryopodded:
            filtered_dinos = {k: v for k, v in filtered_dinos.items() if isinstance(v, TamedDino) and v.cryopod is not None}
            ArkSaveLogger.api_log(f"OnlyCryopodded - Filtered to {len(filtered_dinos)} dinos")

        if stat_minimum is not None:
            new_filtered_dinos = {}
            for key, dino in filtered_dinos.items():
                stats_above = dino.stats.get_of_at_least(stat_minimum, mutated=True)
                if len(stats_above) and (stats is None or any(s in stats_above for s in stats)):
                    new_filtered_dinos[key] = dinos[key]
            filtered_dinos = new_filtered_dinos
            ArkSaveLogger.api_log(f"StatMin - Filtered to {len(filtered_dinos)} dinos")

        return filtered_dinos
    
    def count_by_level(self, List: Dict[UUID, Dino]) -> Dict[int, int]:
        levels = {}

        for key, dino in List.items():
            level = dino.stats.current_level
            if level in levels:
                levels[level] += 1
            else:
                levels[level] = 1

        return levels
    
    def count_by_class(self, List: Dict[UUID, Dino]) -> Dict[str, int]:
        classes = {}

        for key, dino in List.items():
            short_name = dino.get_short_name()
            if short_name in classes:
                classes[short_name] += 1
            else:
                classes[short_name] = 1

        return classes
    
    def count_by_tamed(self, List: Dict[UUID, Dino]) -> Dict[bool, int]:
        tamed = {}

        for key, dino in List.items():
            is_tamed = isinstance(dino, TamedDino)
            if is_tamed in tamed:
                tamed[is_tamed] += 1
            else:
                tamed[is_tamed] = 1

        return tamed
    
    def count_by_cryopodded(self, List: Dict[UUID, Dino]) -> Dict[str, int]:
        cryopodded = {
            "all": 0,
        }

        for key, dino in List.items():
            is_cryopodded = isinstance(dino, TamedDino) and dino.cryopod is not None
            if is_cryopodded:
                short_name = dino.get_short_name()
                cryopodded["all"] += 1
                if short_name in cryopodded:
                    cryopodded[short_name] += 1
                else:
                    cryopodded[short_name] = 1

        return cryopodded
    
    def modify_dinos(self, dinos: Dict[UUID, TamedDino], new_owner: DinoOwner = None, ftp_client: ArkFtpClient = None):
        for key, dino in dinos.items():
            if new_owner is not None:
                dino.owner.replace_with(new_owner, dino.binary)
                dino.update_binary()

        if ftp_client is not None:
            self.save.store_db(TEMP_FILES_DIR / "sapi_temp_save.ark")
            ftp_client.connect()
            ftp_client.upload_save_file(TEMP_FILES_DIR / "sapi_temp_save.ark")
            ftp_client.close()

    def create_heatmap(self, map: ArkMap, resolution: int = 100, dinos: Dict[UUID, TamedDino] = None, classes: List[str] = None, owner: DinoOwner = None, only_tamed: bool = False):
        import math
        import numpy as np

        tamed = None if not only_tamed else True
        if dinos is None:
            dinos = self.get_all_filtered(class_names=classes, tamed=tamed, include_cryopodded=False)

        heatmap = [[0 for _ in range(resolution)] for _ in range(resolution)]
        # print(f"Found {len(dinos)} dinos")

        for key, dino in dinos.items():
            if dino.location is None:
                continue

            coords: MapCoords = dino.location.as_map_coords(map)

            y = math.floor(coords.long)
            x = math.floor(coords.lat)

            if x < 0 or x >= resolution or y < 0 or y >= resolution:
                continue

            heatmap[x][y] += 1

        return np.array(heatmap)
    
    def get_best_dino_for_stat(self, classes: List[str] = None, stat: ArkStat = None, only_tamed: bool = False, only_untamed: bool = False, base_stat: bool = False, mutated_stat=False) -> (Dino, int, ArkStat):
        if only_tamed and only_untamed:
            raise ValueError("Cannot specify both only_tamed and only_untamed")
        
        if mutated_stat and base_stat:
            raise ValueError("Cannot specify both base_stat and base_mutated_stat")
        
        if classes is not None:
            dinos = self.get_all_filtered(class_names=classes, include_cryopodded=True)
        else:
            dinos = self.get_all()

        # print(f"Found {len(dinos)} dinos")

        best_dino = None
        best_value = None
        best_stat = None
        s = stat

        for key, dino in dinos.items():
            if only_tamed and not isinstance(dino, TamedDino):
                continue
            if only_untamed and isinstance(dino, TamedDino):
                continue

            if stat is not None:
                value = dino.stats.get(stat, base_stat, mutated_stat)
            else:
                s, value = dino.stats.get_highest_stat(base_stat, mutated_stat)

            if best_value is None or value > best_value:
                best_value = value
                best_dino = dinos[key]
                best_stat = s

        return best_dino, best_value, best_stat
    
        
    def get_container_of_inventory(self, inv_uuid: UUID, include_cryopodded: bool = True, tamed_dinos: dict[UUID, TamedDino] = None) -> TamedDino:
        if tamed_dinos is None:
            tamed_dinos = self.get_all_tamed(include_cryopodded=include_cryopodded)
        for _, obj in tamed_dinos.items():
            if not isinstance(obj, TamedDino):
                continue
            obj: TamedDino = obj
            if obj.inv_uuid == inv_uuid:
                return obj

        return None

