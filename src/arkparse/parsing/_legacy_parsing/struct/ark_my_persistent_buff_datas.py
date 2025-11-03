import json
from typing import TYPE_CHECKING
from dataclasses import dataclass

from arkparse.utils.json_utils import DefaultJsonEncoder

if TYPE_CHECKING:
    from ..ark_binary_parser import ArkBinaryParser

class ForPrimalBuffClass:
    class64Bit: int
    class_: str

    classString64Bit: int
    class_string: str

    def __init__(self, byte_buffer: "ArkBinaryParser"):
        byte_buffer.validate_string("ForPrimalBuffClass")
        byte_buffer.validate_string("ObjectProperty")

        self.class64Bit = byte_buffer.read_uint64()
        byte_buffer.skip_bytes(1)
        byte_buffer.validate_uint32(1)

        self.class_ = byte_buffer.read_string()

        byte_buffer.validate_string("ForPrimalBuffClassString")
        byte_buffer.validate_string("StrProperty")
        self.classString64Bit = byte_buffer.read_uint64()
        byte_buffer.skip_bytes(1)
        self.class_string = byte_buffer.read_string()

        byte_buffer.validate_string("None")

    def __str__(self):
        return f"ForPrimalBuffClass: {self.class_} {self.class_string}"


@dataclass
class ArkMyPersistentBuffDatas:
    initialIds: list[tuple[int, int]]
    id_: int
    # buffs : list[ForPrimalBuffClass]

    def __init__(self, byte_buffer: "ArkBinaryParser", size: int):
        byte_buffer.validate_uint32(0)
        self.initialIds = []
        
        for i in range(size-1):
            self.initialIds.append((byte_buffer.read_uint32(), byte_buffer.read_uint32()))

        self.initialIds.append((byte_buffer.read_uint32(), 0))

        byte_buffer.validate_string("None")
        byte_buffer.validate_uint32(1)

        self.id_ = str(byte_buffer.read_uint64()) + str(byte_buffer.read_uint64())

        # print("Index is: ", byte_buffer.get_position())
        # self.buffs = []
        # for _ in range(size):
        #     self.buffs.append(ForPrimalBuffClass(byte_buffer)) 
        #     byte_buffer.validate_uint32(0)
            # ArkSaveLogger.open_hex_view(True)

    def __str__(self):
        return f"ArkMyPersistentBuffDatas: {self.id_} {self.initialIds}"

    def to_json_obj(self):
        return { "InitialIDs": self.initialIds, "ID": self.id_ }

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
