import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from struct import pack

from arkparse.utils.json_utils import DefaultJsonEncoder

if TYPE_CHECKING:
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkVector2D:
    x: float = field(default=0.0)
    y: float = field(default=0.0)

    def __init__(self, byte_buffer: "ArkBinaryParser" = None, data_size: int = 16, x: float = 0.0, y: float = 0.0):
        if byte_buffer:
            if data_size <= 8:
                self.x = byte_buffer.read_float()
                self.y = byte_buffer.read_float()
            else:
                self.x = byte_buffer.read_double()
                self.y = byte_buffer.read_double()
        else:
            self.x = x
            self.y = y

    def to_bytes(self) -> bytes:
        return pack('<dd', self.x, self.y)

    def __str__(self):
        return f"Vector2D({self.x:.2f}, {self.y:.2f})"

    def to_json_obj(self):
        return { "x": self.x, "y": self.y }

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
