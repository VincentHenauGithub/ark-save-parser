from dataclasses import dataclass
from typing import TYPE_CHECKING
from arkparse.logging import ArkSaveLogger

if TYPE_CHECKING:   
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkGigantoraptorBondedStruct:
    id1: int
    id2: int
    dino_class: str
    dino_name: str

    def __init__(self, ark_binary_data: "ArkBinaryParser"):
        name = ark_binary_data.peek_name()
        self.id1 = ark_binary_data.parse_int32_property(name)
        name = ark_binary_data.peek_name()
        self.id2 = ark_binary_data.parse_int32_property(name)
        name = ark_binary_data.peek_name()
        self.dino_class = ark_binary_data.parse_soft_object_property(name)
        name = ark_binary_data.peek_name()
        self.dino_name = ark_binary_data.parse_string_property(name)
        ark_binary_data.validate_name("None")

        ArkSaveLogger.parser_log(f"ArkGigantoraptorBondedStruct: {self.dino_class}, {self.dino_name} (ID1: {self.id1}, ID2: {self.id2})")

    def to_json_obj(self):
        return { "id1": self.id1, "id2": self.id2, "dino_class": self.dino_class, "dino_name": self.dino_name }
