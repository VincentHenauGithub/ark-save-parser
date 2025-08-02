import json
from uuid import UUID
import math

from arkparse import AsaSave
from arkparse.logging.ark_save_logger import ArkSaveLogger
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.enums import ArkEquipmentStat
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.utils.json_utils import DefaultJsonEncoder

from .__equipment import Equipment
from .__equipment_with_durability import EquipmentWithDurability


class Weapon(EquipmentWithDurability):
    damage: float = 0

    def __init_props__(self):
        super().__init_props__()

        damage = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.DAMAGE.value, default=0)
        self.damage = self.get_actual_value(ArkEquipmentStat.DAMAGE, damage)

    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)

        self.class_name = "weapon"             

    @staticmethod
    def generate_from_template(class_: str, save: AsaSave, is_bp: bool):
        file = "weapon_bp" if is_bp else "weapon"
        return Equipment._generate_from_template(Weapon, file, class_, save)

    def get_average_stat(self, __stats = []) -> float:
        return super().get_average_stat([self.get_internal_value(ArkEquipmentStat.DAMAGE)])
    
    def get_implemented_stats(self) -> list:
        return super().get_implemented_stats() + [ArkEquipmentStat.DAMAGE]

    def get_internal_value(self, stat: ArkEquipmentStat) -> int:
        if stat == ArkEquipmentStat.DAMAGE:
            value = int((self.damage - 100.0) * 100)
            return value if value >= 100 else 100
        else:
            return super().get_internal_value(stat)    
        
    def get_actual_value(self, stat: ArkEquipmentStat, internal_value: int) -> float:
        if stat == ArkEquipmentStat.DAMAGE:
            return round(100.0 + internal_value / 100, 1)
        else:
            return super().get_actual_value(stat, internal_value)
        
    def set_stat(self, stat: ArkEquipmentStat, value: float):
        if stat == ArkEquipmentStat.DAMAGE:
            self.__set_damage(value)
        else:
            return super().set_stat(stat, value)

    def __set_damage(self, damage: float):
        self.damage = damage
        clipped = self._set_internal_stat_value(self.get_internal_value(ArkEquipmentStat.DAMAGE), ArkEquipmentStat.DAMAGE)
        if clipped:
            self.damage = self.get_actual_value(ArkEquipmentStat.DAMAGE, 65535)
            ArkSaveLogger.warning_log(f"Damage value clipped to {self.damage} for {self.object.blueprint}")

    def auto_rate(self):
        self._auto_rate(0.000674, self.get_average_stat()) 

    def get_stat_for_rating(self, stat: ArkEquipmentStat, rating: float) -> float:
        if stat == ArkEquipmentStat.DAMAGE:
            value = round(rating / 0.000674, 1)
        else:
            value = super()._get_stat_for_rating(stat, rating, 0.000674)

        return self.get_actual_value(stat, value)

    @staticmethod
    def from_inventory_item(item: InventoryItem, save: AsaSave):
        return Equipment.from_inventory_item(item, save, Weapon)

    @staticmethod
    def from_object(obj: ArkGameObject):
        weapon = Weapon()
        weapon.object = obj
        weapon.__init_props__()
        
        return weapon

    def __str__(self):
        return f"Weapon: {self.get_short_name()} - Damage: {self.damage} - Durability: {self.durability} - BP: {self.is_bp} - Crafted: {self.is_crafted()} - Rating: {self.rating}"

    def to_json_obj(self):
        json_obj = super().to_json_obj()
        json_obj["Damage"] = self.damage
        return json_obj

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
