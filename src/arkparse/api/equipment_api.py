from typing import Dict, List
from uuid import UUID
import random

from arkparse.object_model.equipment import Armor, Saddle, Weapon, Shield
from arkparse.object_model.equipment.__equipment import Equipment
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.saves.asa_save import AsaSave
from arkparse.logging import ArkSaveLogger
from arkparse.object_model.misc.object_crafter import ObjectCrafter
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.enums import ArkItemQuality, ArkEquipmentStat
from arkparse.classes.equipment import Equipment as EqClasses

from .general_api import GeneralApi

class EquipmentApi(GeneralApi):
    class Classes:
        WEAPON = Weapon
        SADDLE = Saddle
        ARMOR = Armor
        SHIELD = Shield

    def __init__(self, save: AsaSave):
        config = GameObjectReaderConfiguration(
            blueprint_name_filter=lambda name: name is not None and \
                                               (("Weapons" in name and "PrimalItemAmmo" not in name) or \
                                                 "Armor" in name or \
                                                 name in EqClasses.all_bps)
                                                 
        )
        super().__init__(save, config)
        self.parsed_objects: Dict[UUID, Equipment] = {}

    def __get_cls_filter(self, cls: "EquipmentApi.Classes"):
        if cls == self.Classes.WEAPON:
            return EqClasses.weapons.all_bps
        elif cls == self.Classes.SADDLE:
            return EqClasses.saddles.all_bps
        elif cls == self.Classes.ARMOR:
            return EqClasses.armor.all_bps
        elif cls == self.Classes.SHIELD:
            return EqClasses.shield.all_bps
        else:
            return None
    
    def get_all(self, cls: "EquipmentApi.Classes", config: GameObjectReaderConfiguration = None) -> Dict[UUID, Equipment]:
        def is_valid(obj: ArkGameObject):
            is_engram = obj.get_property_value("bIsEngram")
            return not is_engram
        
        _config = GameObjectReaderConfiguration(
            blueprint_name_filter=lambda name: (True if config is None else config.blueprint_name_filter(name)) and name in self.__get_cls_filter(cls)
        )

        return super().get_all(cls, valid_filter=is_valid, config=_config)
    
    def get_by_class(self, cls: "EquipmentApi.Classes", classes: List[str]) -> Dict[UUID, Equipment]:
        config = GameObjectReaderConfiguration(
            blueprint_name_filter=lambda name: name is not None and name in classes and name in self.__get_cls_filter(cls)
        )

        return self.get_all(cls, config)
    
    def get_filtered(self, cls: "EquipmentApi.Classes", 
                     no_bluepints: bool = None, only_blueprints: bool = None, 
                     minimum_quality: ArkItemQuality = ArkItemQuality.PRIMITIVE,
                     crafter: ObjectCrafter = None,
                     classes: List[str] = None) -> Dict[UUID, Equipment]:
        if no_bluepints and only_blueprints:
            raise ValueError("Cannot filter by both no_blueprints and only_blueprints")

        if classes is not None:
            equipment: Dict[UUID, Equipment] = self.get_by_class(cls, classes)
        else:
            equipment: Dict[UUID, Equipment] = self.get_all(cls)

        if no_bluepints:
            equipment = {uuid: item for uuid, item in equipment.items() if not item.is_bp}

        if only_blueprints:
            equipment = {uuid: item for uuid, item in equipment.items() if item.is_bp}

        if minimum_quality != ArkItemQuality.PRIMITIVE:
            equipment = {uuid: item for uuid, item in equipment.items() if item.quality >= minimum_quality.value}

        if crafter is not None:
            equipment = {uuid: item for uuid, item in equipment.items() if item.crafter == crafter}

        return equipment
    
    
    def get_count(self, items: Dict[UUID, InventoryItem]) -> int:
        count = 0
        for item in items.values():
            count += item.quantity
        return count
    
    def get_saddles(self, classes: List[str] = None, minimum_armor: int = None, minimum_durability: int = None) -> Dict[UUID, Saddle]:
        saddles: Dict[UUID, Saddle] = self.get_filtered(self.Classes.SADDLE, classes=classes)
        
        if minimum_armor is not None:
            saddles = {uuid: saddle for uuid, saddle in saddles.items() if saddle.armor >= minimum_armor}
        
        if minimum_durability is not None:
            saddles = {uuid: saddle for uuid, saddle in saddles.items() if saddle.durability >= minimum_durability}
        
        return saddles

    def get_weapons(self, classes: List[str] = None, minimum_damage: int = None, minimum_durability: int = None) -> Dict[UUID, Weapon]:
        weapons: Dict[UUID, Weapon] = self.get_filtered(self.Classes.WEAPON, classes=classes)
        
        if minimum_damage is not None:
            weapons = {uuid: weapon for uuid, weapon in weapons.items() if weapon.damage >= minimum_damage}
        
        if minimum_durability is not None:
            weapons = {uuid: weapon for uuid, weapon in weapons.items() if weapon.durability >= minimum_durability}
        
        return weapons
    
    def get_armor(self, classes: List[str] = None, minimum_armor: int = None, minimum_durability: int = None, minimum_cold_resistance: int = None, minimum_heat_resistance: int = None) -> Dict[UUID, Armor]:
        armor: Dict[UUID, Armor] = self.get_filtered(self.Classes.ARMOR, classes=classes)
        
        if minimum_armor is not None:
            armor = {uuid: armor_piece for uuid, armor_piece in armor.items() if armor_piece.armor >= minimum_armor}
        
        if minimum_durability is not None:
            armor = {uuid: armor_piece for uuid, armor_piece in armor.items() if armor_piece.durability >= minimum_durability}
        
        if minimum_cold_resistance is not None:
            armor = {uuid: armor_piece for uuid, armor_piece in armor.items() if armor_piece.hypothermal_insulation >= minimum_cold_resistance}
        
        if minimum_heat_resistance is not None:
            armor = {uuid: armor_piece for uuid, armor_piece in armor.items() if armor_piece.hyperthermal_insulation >= minimum_heat_resistance}
        
        return armor
    
    def get_shields(self, classes: List[str] = None, minimum_armor: int = None, minimum_durability: int = None) -> Dict[UUID, Shield]:
        shields: Dict[UUID, Shield] = self.get_filtered(self.Classes.SHIELD, classes=classes)
        
        if minimum_armor is not None:
            shields = {uuid: shield for uuid, shield in shields.items() if shield.armor >= minimum_armor}
        
        if minimum_durability is not None:
            shields = {uuid: shield for uuid, shield in shields.items() if shield.durability >= minimum_durability}
        
        return shields
    
    def modify_equipment(self, eq_class_ : "EquipmentApi.Classes", equipment: Equipment, target_class: str = None, target_stat: ArkEquipmentStat = None, value: float = None, range: tuple[float, float] = None):
        if eq_class_ == self.Classes.WEAPON:
            equipment: Weapon
        elif eq_class_ == self.Classes.SADDLE:
            equipment: Saddle
        elif eq_class_ == self.Classes.ARMOR:
            equipment: Armor
        elif eq_class_ == self.Classes.SHIELD:
            equipment: Shield
        else:
            raise ValueError("Invalid class")
        
        equipment.reidentify(new_class=target_class)
        equipment._set_internal_stat_value

    def __get_internal_value_range(self, equipment: Equipment, stat: ArkEquipmentStat, min_value: float, max_value: float) -> tuple[float, float]:
        equipment.set_stat(stat, min_value)
        min_internal = equipment.get_internal_value(stat)
        equipment.set_stat(stat, max_value)
        max_internal = equipment.get_internal_value(stat)
        return min_internal, max_internal


    def generate_equipment(self, eq_class_ : "EquipmentApi.Classes", blueprint: str, master_stat: ArkEquipmentStat, min_value: float, max_value: float, force_bp: bool = None, from_rating: bool = False, normal_distribution: bool = False, bp_chance: float = 0.3) -> Equipment:

        # Generate equipment based on the specified class and blueprint
        bp_chance_yes = bp_chance * 100 if force_bp is None else 0 if force_bp else 100
        bp_chance_no = 100 - bp_chance_yes
        is_bp = random.choices([True, False], weights=[bp_chance_yes, bp_chance_no], k=1)[0]
        equipment: Equipment = eq_class_.generate_from_template(blueprint, self.save, is_bp=is_bp)

        if from_rating:
            ArkSaveLogger.api_log(f"from rating {min_value} to {max_value} for {master_stat}")
            min_value = equipment.get_stat_for_rating(master_stat, min_value)
            max_value = equipment.get_stat_for_rating(master_stat, max_value)

        range_min, range_max = self.__get_internal_value_range(equipment, master_stat, min_value, max_value)
        ArkSaveLogger.api_log(f"Internal value range for {master_stat} is [{range_min}, {range_max}]")
        
        if normal_distribution:
            mu    = (range_min + range_max) / 2
            sigma = (range_max - range_min) / (2 * 1.64485)  # ≈ (range_max - range_min) / 3.2897 about 90% 

        for stat in equipment.get_implemented_stats():
            if normal_distribution:
                random_value = int(random.gauss(mu, sigma))
            else:
                random_value = int(random.uniform(range_min, range_max))

            if random_value < range_min:
                random_value = range_min
            elif random_value > range_max*1.5:
                random_value = int(range_max*1.5)

            ArkSaveLogger.api_log(f"Setting {stat} to {random_value} for {equipment.class_name} {"(used normal distribution)" if normal_distribution else "(used uniform distribution)"}")
            equipment.set_stat(stat, equipment.get_actual_value(stat, random_value))

        equipment.auto_rate()

        return equipment

            