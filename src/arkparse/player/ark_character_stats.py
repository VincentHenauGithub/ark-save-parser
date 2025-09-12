import json
from typing import List
from dataclasses import dataclass, field

from arkparse.parsing.ark_property import ArkProperty
from arkparse.parsing import ArkPropertyContainer
from arkparse.parsing.struct import ObjectReference
from arkparse.utils.json_utils import DefaultJsonEncoder


@dataclass
class ArkStatPoints:
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
    crafting_speed: int = 0  # Optional: Adjust if not present

    def __init__(self, properties: List[ArkProperty]):
        # Define a mapping from property position to stat attribute
        position_map = {
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

        for prop in properties:
            if prop.type not in ["Byte", "Int"]:
                continue  # Skip properties of unexpected types
            stat_name = position_map.get(prop.position)
            if stat_name:
                setattr(self, stat_name, prop.value)

    def __str__(self):
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
        return f"ArkStatPoints(points added)([{', '.join(stats)}])"

    def to_json_obj(self):
        return { "Health": self.health,
                 "Stamina": self.stamina,
                 "Torpidity": self.torpidity,
                 "Oxygen": self.oxygen,
                 "Food": self.food,
                 "Water": self.water,
                 "Temperature": self.temperature,
                 "Weight": self.weight,
                 "MeleeDamage": self.melee_damage,
                 "MovementSpeed": self.movement_speed,
                 "Fortitude": self.fortitude,
                 "CraftingSpeed": self.crafting_speed }

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)


@dataclass
class ArkCharacterStats:
    level: int = 0
    experience: float = 0.0
    engram_points: int = 0
    explorer_notes: List[int] = field(default_factory=list)
    emotes: List[str] = field(default_factory=list)
    engrams: List[str] = field(default_factory=list)
    stats: ArkStatPoints = field(default_factory=lambda: ArkStatPoints([]))

    def __init__(self, properties: ArkPropertyContainer):

        # Find the main struct property, assumed to be "MyPersistentCharacterStats"
        # main_stats_prop = properties.find_property("MyPersistentCharacterStats")
        # if not main_stats_prop:
        #     raise ValueError("Missing 'MyPersistentCharacterStats' property.")
        # if main_stats_prop.type != "Struct":
        #     raise ValueError("'MyPersistentCharacterStats' is not of type 'Struct'.")

        main_properties: ArkPropertyContainer = properties

        self.level = 1 + main_properties.get_property_value("CharacterStatusComponent_ExtraCharacterLevel", 0)
        self.experience = main_properties.get_property_value("CharacterStatusComponent_ExperiencePoints", 0.0)
        self.engram_points = main_properties.get_property_value("PlayerState_TotalEngramPoints", 0)
        self.explorer_notes = main_properties.get_array_property_value("PerMapExplorerNoteUnlocks", [])
        self.emotes = main_properties.get_array_property_value("EmoteUnlocks", [])
        self.engrams = main_properties.get_array_property_value("PlayerState_EngramBlueprints", [])

        # print(f"ArkCharacterStats: Level={self.level}, Experience={self.experience}, Engram Points={self.engram_points}")

        # Parse stats
        stat_points_props = main_properties.find_all_properties_of_name("CharacterStatusComponent_NumberOfLevelUpPointsApplied")
        if stat_points_props:
            self.stats = ArkStatPoints(stat_points_props)
        else:
            self.stats = ArkStatPoints([])

    def __str__(self):
        """
        Returns a compact string representation of ArkCharacterStats.

        Returns:
            str: String representation of the character stats.
        """
        parts = [
            "ArkCharacterStats:",
            f"  Level: {self.level}",
            f"  Experience: {self.experience}",
            f"  Engram Points: {self.engram_points}",
            f"  Explorer Notes: {self.explorer_notes}",
            f"  Emotes: {self.emotes}",
            f"  Engrams: {len(self.engrams)} engrams",
            f"  Stats: {self.stats}"
        ]
        return "\n".join(parts)

    def to_json_obj(self):
        return { "CharacterStatusComponent_ExtraCharacterLevel": self.level,
                 "CharacterStatusComponent_ExperiencePoints": self.experience,
                 "PlayerState_TotalEngramPoints": self.engram_points,
                 "PerMapExplorerNoteUnlocks": self.explorer_notes,
                 "EmoteUnlocks": self.emotes,
                 "PlayerState_EngramBlueprints": self.engrams,
                 "CharacterStatusComponent_NumberOfLevelUpPointsApplied": self.stats.to_json_obj() if self.stats is not None else None }

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
