import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from arkparse.utils.json_utils import DefaultJsonEncoder

if TYPE_CHECKING:
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkUniqueNetIdRepl:
    unknown: int
    value_type: str
    value: str

    def __init__(self, byte_buffer: "ArkBinaryParser"):
        # print(f"Reading ArkUniqueNetIdRepl at {byte_buffer.get_position()}")
        self.unknown = byte_buffer.read_byte()
        self.value_type = byte_buffer.read_string()
        length = byte_buffer.read_byte()
        self.value = byte_buffer.read_bytes_as_hex(length).replace(' ', '').lower()

    def __str__(self):
        return f"ArkUniqueNetIdRepl: {self.value_type} {self.value}"

    def to_json_obj(self):
        return { "unknown": self.unknown, "value_type": self.value_type, "value": self.value }

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
