import json
from uuid import UUID
import os

from arkparse import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.logging import ArkSaveLogger
from arkparse.enums import ArkEquipmentStat
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.utils.json_utils import DefaultJsonEncoder

from .__equipment import Equipment
from .__equipment_with_armor import EquipmentWithArmor
from .__armor_defaults import  _get_default_hypoT, _get_default_hyperT


class Armor(EquipmentWithArmor):
    armor: float = 0
    hypothermal_insulation: float = 0
    hyperthermal_insulation: float = 0

    def __init_props__(self):
        super().__init_props__()
            
        hypo = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.HYPOTHERMAL_RESISTANCE.value, default=0)
        hyper = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.HYPERTHERMAL_RESISTANCE.value, default=0)

        self.hypothermal_insulation = self.get_actual_value(ArkEquipmentStat.HYPOTHERMAL_RESISTANCE, hypo)
        self.hyperthermal_insulation = self.get_actual_value(ArkEquipmentStat.HYPERTHERMAL_RESISTANCE, hyper)

    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)
                         
        self.class_name = "armor"

    @staticmethod
    def generate_from_template(class_: str, save: AsaSave, is_bp: bool):
        file = "armor_bp" if is_bp else "armor"
        return Equipment._generate_from_template(Armor, file, class_, save)

    def get_average_stat(self, __stats = []) -> float:
        return super().get_average_stat(__stats + [self.get_internal_value(ArkEquipmentStat.HYPOTHERMAL_RESISTANCE),
                                                   self.get_internal_value(ArkEquipmentStat.HYPERTHERMAL_RESISTANCE)])
    
    def get_implemented_stats(self) -> list:
        return super().get_implemented_stats() + [ArkEquipmentStat.HYPOTHERMAL_RESISTANCE, ArkEquipmentStat.HYPERTHERMAL_RESISTANCE]

    def get_internal_value(self, stat: ArkEquipmentStat) -> int:
        if stat == ArkEquipmentStat.HYPOTHERMAL_RESISTANCE:
            if self.hypothermal_insulation == 0:
                return 0
            d = _get_default_hypoT(self.object.blueprint)
            value = int((self.hypothermal_insulation - d)/(d*0.0002))
            return value if value >= d else d
        elif stat == ArkEquipmentStat.HYPERTHERMAL_RESISTANCE:
            if self.hyperthermal_insulation == 0:
                return 0
            d = _get_default_hyperT(self.object.blueprint)
            value = int((self.hyperthermal_insulation - d)/(d*0.0002))
            return value if value >= d else d
        else:
            return super().get_internal_value(stat)
        
    def get_actual_value(self, stat: ArkEquipmentStat, internal_value: int) -> float:
        if stat == ArkEquipmentStat.HYPOTHERMAL_RESISTANCE:
            if internal_value == 0:
                return 0
            d = _get_default_hypoT(self.object.blueprint)
            return round(d*(0.0002*internal_value + 1), 1)
        elif stat == ArkEquipmentStat.HYPERTHERMAL_RESISTANCE:
            if internal_value == 0:
                return 0
            d = _get_default_hyperT(self.object.blueprint)
            return round(d*(0.0002*internal_value + 1), 1)
        else:
            return super().get_actual_value(stat, internal_value)
        
    def set_stat(self, stat: ArkEquipmentStat, value: float):
        if stat == ArkEquipmentStat.HYPOTHERMAL_RESISTANCE:
            self.__set_hypothermal_insulation(value)
        elif stat == ArkEquipmentStat.HYPERTHERMAL_RESISTANCE:
            self.__set_hyperthermal_insulation(value)
        else:
            return super().set_stat(stat, value)

    def __set_hypothermal_insulation(self, hypoT: float):
        self.hypothermal_insulation = hypoT
        clipped = self._set_internal_stat_value(self.get_internal_value(ArkEquipmentStat.HYPOTHERMAL_RESISTANCE), ArkEquipmentStat.HYPOTHERMAL_RESISTANCE)
        if clipped:
            self.hypothermal_insulation = self.get_actual_value(ArkEquipmentStat.HYPOTHERMAL_RESISTANCE, 65535)
            ArkSaveLogger.warning_log(f"Hypothermal insulation value clipped to {self.hypothermal_insulation} for {self.object.blueprint}")

    def __set_hyperthermal_insulation(self, hyperT: float):
        self.hyperthermal_insulation = hyperT
        clipped = self._set_internal_stat_value(self.get_internal_value(ArkEquipmentStat.HYPERTHERMAL_RESISTANCE), ArkEquipmentStat.HYPERTHERMAL_RESISTANCE)
        if clipped:
            self.hyperthermal_insulation = self.get_actual_value(ArkEquipmentStat.HYPERTHERMAL_RESISTANCE, 65535)
            ArkSaveLogger.warning_log(f"Hyperthermal insulation value clipped to {self.hyperthermal_insulation} for {self.object.blueprint}")

    def auto_rate(self):
        self._auto_rate(0.000760, self.get_average_stat())

    def get_stat_for_rating(self, stat: ArkEquipmentStat, rating: float) -> float:
        if stat == ArkEquipmentStat.HYPOTHERMAL_RESISTANCE or stat == ArkEquipmentStat.HYPERTHERMAL_RESISTANCE:
            value = round(rating / 0.000760, 1)
        else:
            value = super()._get_stat_for_rating(stat, rating, 0.000760)
        
        return self.get_actual_value(stat, value)

    @staticmethod
    def from_inventory_item(item: InventoryItem, save: AsaSave):
        return Equipment.from_inventory_item(item, save, Armor)

    @staticmethod
    def from_object(obj: ArkGameObject):
        armor = Armor()
        armor.object = obj
        armor.__init_props__()
        
        return armor
    
    def __str__(self):
        return f"Armor: {self.get_short_name()} - Armor: {self.armor} - Durability: {self.durability} - HypoT: {self.hypothermal_insulation} - HyperT: {self.hyperthermal_insulation} - BP: {self.is_bp} - Crafted: {self.is_crafted()} - Quality: {self.quality} - Rating: {self.rating}"

    def to_json_obj(self):
        json_obj = super().to_json_obj()
        json_obj["HyperthermalResistance"] = self.hyperthermal_insulation
        json_obj["HypothermalResistance"] = self.hypothermal_insulation
        return json_obj

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
