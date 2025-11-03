import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from arkparse.utils.json_utils import DefaultJsonEncoder

if TYPE_CHECKING:
    from ..ark_binary_parser import ArkBinaryParser

@dataclass
class ArkVector:
    x: float = field(default=0.0)
    y: float = field(default=0.0)
    z: float = field(default=0.0)

    def __init__(self, byte_buffer: "ArkBinaryParser" = None, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        if byte_buffer:
            self.x = byte_buffer.read_double()
            self.y = byte_buffer.read_double()
            self.z = byte_buffer.read_double()
        else:
            self.x = x
            self.y = y
            self.z = z
    
    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    def to_json_obj(self):
        return { "x": self.x, "y": self.y, "z": self.z }

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
