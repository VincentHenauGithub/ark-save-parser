from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID
from arkparse.logging import ArkSaveLogger
from .ark_vector import ArkVector
from .ark_rotator import ArkRotator

if TYPE_CHECKING:   
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkPrimalSaddleStructure:
    location: ArkVector = None
    rotation: ArkRotator = None
    bone_name: str = ""
    my_structure: UUID = None


    def __init__(self, ark_binary_data: "ArkBinaryParser"):
        ark_binary_data.validate_name("DinoRelativeLocation")
        self.location = ArkVector(ark_binary_data, from_struct=True)
        ark_binary_data.validate_name("DinoRelativeRotation")
        self.rotation = ArkRotator(ark_binary_data, from_struct=True)
        self.bone_name = ark_binary_data.parse_name_property("BoneName")
        ark_binary_data.validate_name("MyStructure")
        ark_binary_data.validate_name("ObjectProperty")
        ark_binary_data.validate_uint32(0)
        ark_binary_data.validate_uint32(0x12)
        ark_binary_data.validate_byte(0)
        ark_binary_data.validate_uint16(0)
        self.my_structure = ark_binary_data.read_uuid()
        ark_binary_data.validate_name("None")

        ArkSaveLogger.parser_log(f"ArkPrimalSaddleStructure: {self.location}, {self.rotation}, {self.bone_name}, {self.my_structure}")

    def to_json_obj(self):
        return { "location": self.location.to_json_obj(), "rotation": self.rotation.to_json_obj(), "bone_name": self.bone_name, "my_structure": self.my_structure.__str__() }
