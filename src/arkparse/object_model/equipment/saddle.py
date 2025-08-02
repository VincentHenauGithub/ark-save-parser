import json
from uuid import UUID

from arkparse import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.enums import ArkEquipmentStat
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.utils.json_utils import DefaultJsonEncoder

from .__equipment import Equipment
from .__equipment_with_armor import EquipmentWithArmor

class Saddle(EquipmentWithArmor):
    def __init_props__(self):
        super().__init_props__()

    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)
        self.class_name = "saddle"             
    
    @staticmethod
    def generate_from_template(class_: str, save: AsaSave, is_bp: bool):
        file = "saddle_bp" if is_bp else "saddle"
        eq = Equipment._generate_from_template(Saddle, file, class_, save)
        return eq
    
    def auto_rate(self):
        self._auto_rate(0.000926, self.get_average_stat())

    def get_stat_for_rating(self, stat: ArkEquipmentStat, rating: float) -> float:
        value = super()._get_stat_for_rating(stat, rating, 0.000926)
        return self.get_actual_value(stat, value)

    @staticmethod
    def from_inventory_item(item: InventoryItem, save: AsaSave):
        return Equipment.from_inventory_item(item, save, Saddle)

    @staticmethod
    def from_object(obj: ArkGameObject):
        saddle = Saddle()
        saddle.object = obj
        saddle.__init_props__()
        
        return saddle

    def __str__(self):
        return f"Saddle: {self.get_short_name()} - Armor: {self.armor} - Durability: {self.durability} - BP: {self.is_bp} - Crafted: {self.is_crafted()}"

    def to_json_obj(self):
        return super().to_json_obj()

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
