import json
from uuid import UUID

from arkparse import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.enums import ArkEquipmentStat
from arkparse.utils.json_utils import DefaultJsonEncoder
from .__equipment_with_durability import EquipmentWithDurability

class Shield(EquipmentWithDurability):
    def __init_props__(self):
        super().__init_props__()

    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)
        self.class_name = "shield"

    def auto_rate(self):
        self._auto_rate(0.000519, self.get_average_stat())    

    def get_stat_for_rating(self, stat: ArkEquipmentStat, rating: float) -> float:
        value = super()._get_stat_for_rating(stat, rating, 0.000519)
        return self.get_actual_value(stat, value)
    
    @staticmethod
    def generate_from_template(class_: str, save: AsaSave, is_bp: bool):
        file = "shield_bp" if is_bp else "shield"
        eq = EquipmentWithDurability._generate_from_template(Shield, file, class_, save)
        return eq

    @staticmethod
    def from_object(obj: ArkGameObject):
        shield = Shield()
        shield.object = obj
        shield.__init_props__()
        
        return shield

    def __str__(self):
        return f"Shield: {self.get_short_name()} - CurrentDurability: {self.current_durability} - Durability: {self.durability} - BP: {self.is_bp} - Crafted: {self.is_crafted()} - Rating: {self.rating}"

    def to_json_obj(self):
        return super().to_json_obj()

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
