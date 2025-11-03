import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from struct import pack

from arkparse.utils.json_utils import DefaultJsonEncoder

if TYPE_CHECKING:
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkVector:
    x: float = field(default=0.0)
    y: float = field(default=0.0)
    z: float = field(default=0.0)

    def __init__(self, byte_buffer: "ArkBinaryParser" = None, x: float = 0.0, y: float = 0.0, z: float = 0.0, from_struct: bool = False):
        if from_struct:
            byte_buffer.validate_name("StructProperty")
            byte_buffer.validate_uint32(1)
            byte_buffer.validate_name("Vector")
            byte_buffer.validate_uint32(1)
            byte_buffer.validate_name("/Script/CoreUObject")
            byte_buffer.validate_uint32(0)
            byte_buffer.validate_uint32(0x18)
            byte_buffer.validate_byte(8)

        if byte_buffer:
            self.x = byte_buffer.read_double()
            self.y = byte_buffer.read_double()
            self.z = byte_buffer.read_double()
        else:
            self.x = x
            self.y = y
            self.z = z

    def to_bytes(self) -> bytes:
        return pack('<ddd', self.x, self.y, self.z)

    def __str__(self):
        return f"Vector({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"

    def to_json_obj(self):
        return { "x": self.x, "y": self.y, "z": self.z }

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
