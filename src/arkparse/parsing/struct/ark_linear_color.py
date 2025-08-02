from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkLinearColor:
    r: float
    g: float
    b: float
    a: float

    def __init__(self, byte_buffer: "ArkBinaryParser"):
        self.r = byte_buffer.read_float()
        self.g = byte_buffer.read_float()
        self.b = byte_buffer.read_float()
        self.a = byte_buffer.read_float()

    def to_json_obj(self):
        return { "r": self.r, "g": self.g, "b": self.b, "a": self.a }
