from typing import List
from dataclasses import dataclass
from uuid import UUID

from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase
from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.enums import ArkStat

STAT_POSITION_MAP = {
    0: 'health',
    1: 'stamina',
    2: 'torpidity',
    3: 'oxygen',
    4: 'food',
    5: 'water',
    6: 'temperature',
    7: 'weight',
    8: 'melee_damage',
    9: 'movement_speed',
    10: 'fortitude',
    11: 'crafting_speed'
}

@dataclass
class StatPoints:
    health: int = 0
    stamina: int = 0
    torpidity: int = 0
    oxygen: int = 0
    food: int = 0
    water: int = 0
    temperature: int = 0
    weight: int = 0
    melee_damage: int = 0
    movement_speed: int = 0
    fortitude: int = 0
    crafting_speed: int = 0
    type: str = "NumberOfLevelUpPointsApplied"

    def __init__(self, object: ArkGameObject = None, type: str = "NumberOfLevelUpPointsApplied"):
        self.type = type

        if object is None:
            return

        for idx, stat in STAT_POSITION_MAP.items():
            value = object.get_property_value(self.type, position=idx)
            setattr(self, stat, 0 if value is None else value)

    def __type_str(self):
        "base points" if self.type == "NumberOfLevelUpPointsApplied" else "points added"

    def get_level(self):
        return self.health + self.stamina + self.torpidity + self.oxygen + self.food + \
               self.water + self.temperature + self.weight + self.melee_damage + \
               self.movement_speed + self.fortitude + self.crafting_speed + (1 if self.type == "NumberOfLevelUpPointsApplied" else 0)

    def __str__(self):
        stats = [
            f"health={self.health}",
            f"stamina={self.stamina}",
            f"oxygen={self.oxygen}",
            f"food={self.food}",
            f"weight={self.weight}",
            f"melee_damage={self.melee_damage}",
        ]
        return f"Statpoints({self.__type_str()})([{', '.join(stats)}])"
    
    def to_string_all(self):
        stats = [
            f"health={self.health}",
            f"stamina={self.stamina}",
            f"torpidity={self.torpidity}",
            f"oxygen={self.oxygen}",
            f"food={self.food}",
            f"water={self.water}",
            f"temperature={self.temperature}",
            f"weight={self.weight}",
            f"melee_damage={self.melee_damage}",
            f"movement_speed={self.movement_speed}",
            f"fortitude={self.fortitude}",
            f"crafting_speed={self.crafting_speed}",
        ]
        return f"Statpoints({self.__type_str()})([{', '.join(stats)}])"

@dataclass
class StatValues:
    health: float = 0
    stamina: float = 0
    torpidity: float = 0
    oxygen: float = 0
    food: float = 0
    water: float = 0
    temperature: float = 0
    weight: float = 0
    melee_damage: float = 0
    movement_speed: float = 0
    fortitude: float = 0
    crafting_speed: float = 0

    def __init__(self, object: ArkGameObject = None):
        if object is None:
            return
        
        for idx, stat in STAT_POSITION_MAP.items():
            value = object.get_property_value("CurrentStatusValues", position=idx)
            setattr(self, stat, 0 if value is None else value)

    def __str__(self):
        stats = [
            f"health={self.health}",
            f"stamina={self.stamina}",
            f"oxygen={self.oxygen}",
            f"food={self.food}",
            f"weight={self.weight}",
            f"melee_damage={self.melee_damage}",
            f"torpor={self.torpidity}",
        ]
        return f"Statvalues(points added)([{', '.join(stats)}])"
    
    def to_string_all(self):
        stats = [
            f"health={self.health}",
            f"stamina={self.stamina}",
            f"torpidity={self.torpidity}",
            f"oxygen={self.oxygen}",
            f"food={self.food}",
            f"water={self.water}",
            f"temperature={self.temperature}",
            f"weight={self.weight}",
            f"melee_damage={self.melee_damage}",
            f"movement_speed={self.movement_speed}",
            f"fortitude={self.fortitude}",
            f"crafting_speed={self.crafting_speed}",
        ]
        return f"Statvalues(points added)([{', '.join(stats)}])"
    
class DinoStats(ParsedObjectBase):
    base_level: int = 0
    current_level: int = 0

    base_stat_points: StatPoints = StatPoints()
    added_stat_points: StatPoints = StatPoints(type="NumberOfLevelUpPointsAppliedTamed")
    mutated_stat_points: StatPoints = StatPoints(type="NumberOfMutationsAppliedTamed")
    stat_values: StatValues = StatValues()
    _percentage_imprinted: float

    def __init_props__(self):
        super().__init_props__()

        base_lv = self.object.get_property_value("BaseCharacterLevel")
        self.base_level = 0 if base_lv is None else base_lv
        self.base_stat_points = StatPoints(self.object)
        self.added_stat_points = StatPoints(self.object, "NumberOfLevelUpPointsAppliedTamed")
        self.mutated_stat_points = StatPoints(self.object, "NumberOfMutationsAppliedTamed")
        self.stat_values = StatValues(self.object)
        self.current_level = self.base_stat_points.get_level() + self.added_stat_points.get_level() + self.mutated_stat_points.get_level()
        self._percentage_imprinted = self.object.get_property_value("DinoImprintingQuality", 0.0) * 100
    
    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)

    @staticmethod
    def from_object(obj: ArkGameObject):
        s: DinoStats = DinoStats()
        s.object = obj
        s.__init_props__()

        return s

    def __str__(self):
        return f"DinoStats(level={self.current_level})"
    
    def get(self, stat: ArkStat, base: bool = False, mutated: bool = False):
        if base and mutated:
            raise ValueError("Cannot get base and mutated stats at the same time")

        return (getattr(self.base_stat_points, STAT_POSITION_MAP[stat.value]) + \
                (0 if base else getattr(self.mutated_stat_points, STAT_POSITION_MAP[stat.value]))) + \
                (0 if (base or mutated) else getattr(self.added_stat_points, STAT_POSITION_MAP[stat.value]))

    def get_of_at_least(self, value: float, base: bool = False, mutated: bool = False) -> List[ArkStat]:
        stats = []
        for stat in ArkStat:
            if self.get(stat,base, mutated) >= value:
                stats.append(stat)
        return stats
    
    def stat_to_string(self, stat: ArkStat):
        return f"{self.stat_name_string(stat)}={self.get(stat, False, False)}"
    
    def stat_name_string(self, stat: ArkStat):
        return f"{STAT_POSITION_MAP[stat.value]}"
    
    def to_string_all(self):
        return f"DinoStats(base_level={self.base_level}, " + \
               f"level={self.current_level}, " + \
               f"\nbase stats={self.base_stat_points.to_string_all()}, " + \
               f"\nadded stats={self.added_stat_points.to_string_all()}, " + \
               f"\nstat_values={self.stat_values.to_string_all()})"
    
    def get_highest_stat(self, base: bool = False, mutated: bool = False):
        highest = 0
        best_stat = None
        for stat in ArkStat:
            value = self.get(stat, base, mutated)
            if value > highest:
                highest = value
                best_stat = stat
        return best_stat, highest
    
    def get_mutations(self, stat: ArkStat):
        return getattr(self.mutated_stat_points, STAT_POSITION_MAP[stat.value]) / 2
    
    def get_total_mutations(self):
        return self.mutated_stat_points.get_level() / 2
    
    def modify_stat_value(self, stat: ArkStat, value: float):
        setattr(self.stat_values, STAT_POSITION_MAP[stat.value], value)

        prop = self.object.find_property("CurrentStatusValues", stat.value)
        self.binary.replace_float(prop, value)

        self.update_binary()

    def modify_stat_points(self, stat: ArkStat, value: int):
        setattr(self.base_stat_points, STAT_POSITION_MAP[stat.value], value)

        prop = self.object.find_property("NumberOfLevelUpPointsApplied", stat.value)
        self.binary.replace_byte_property(prop, value)

        new_level = self.base_stat_points.get_level()
        self.base_level = new_level
        prop = self.object.find_property("BaseCharacterLevel")
        self.binary.replace_u32(prop, new_level)

        self.update_binary()

    def modify_experience(self, value: int):
        prop = self.object.find_property("ExperiencePoints")
        self.binary.replace_float(prop, value)

        self.update_binary()

    def prevent_level_up(self):
        if self.object.get_property_value("bAllowLevelUps") == True:
            prop = self.object.find_property("bAllowLevelUps")
            self.binary.replace_boolean(prop, False)

            self.update_binary()
