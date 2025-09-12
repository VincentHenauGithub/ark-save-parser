import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arkparse.object_model.ark_game_object import ArkGameObject
    from arkparse.parsing.ark_binary_parser import ArkBinaryParser

class DinoId:
    id1: int
    id2: int

    def __init__(self, id1: int, id2: int):
        self.id1 = id1
        self.id2 = id2

    @classmethod
    def generate(cls):
        new_id_1 = random.randint(0, 2**31 - 1)
        new_id_2 = random.randint(0, 2**31 - 1)
        return cls(new_id_1, new_id_2)
    
    @classmethod
    def from_data(cls, object: "ArkGameObject"):
        id1 = object.get_property_value("DinoID1")
        id2 = object.get_property_value("DinoID2")
        return cls(id1, id2)
    
    def replace(self, binary: "ArkBinaryParser", object: "ArkGameObject"):
        binary.replace_u32(object.find_property("DinoID1"), self.id1)
        binary.replace_u32(object.find_property("DinoID2"), self.id2)
        
    def __hash__(self):
        return hash((self.id1, self.id2))
    
    def __str__(self):
        return f"DinoId:({self.id1}, {self.id2})"
    
    def __eq__(self, other):
        if not isinstance(other, DinoId):
            return False
        return self.id1 == other.id1 and self.id2 == other.id2
