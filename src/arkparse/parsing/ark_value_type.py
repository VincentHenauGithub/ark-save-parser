from enum import Enum
from typing import Type, Optional, Any
from decimal import Decimal
from arkparse.enums.ark_enum import ArkEnumValue
from .ark_set import ArkSet

class ArkValueType(Enum):
    Boolean = ("BoolProperty", bool)
    Byte = ("ByteProperty", int)
    Float = ("FloatProperty", float)
    Int = ("IntProperty", int)
    Enum = ("EnumProperty", ArkEnumValue)
    Name = ("NameProperty", str)
    Object = ("ObjectProperty", str)
    String = ("StrProperty", str)
    Struct = ("StructProperty", object)  # Placeholder for custom struct
    Array = ("ArrayProperty", list)
    Double = ("DoubleProperty", float)
    Int16 = ("Int16Property", int)  # Python's int serves for both Int16 and regular integers
    Int64 = ("Int64Property", int)
    Int8 = ("Int8Property", int)
    UInt16 = ("UInt16Property", int)
    UInt32 = ("UInt32Property", int)
    UInt64 = ("UInt64Property", Decimal)  # Use Decimal for very large unsigned integers
    SoftObject = ("SoftObjectProperty", str)
    Set = ("SetProperty", ArkSet)
    Map = ("MapProperty", "ArkProperty")  # Use a string annotation for ArkProperty to prevent circular imports

    def __init__(self, type_name: str, clazz: Type[Any]):
        self._type_name = type_name
        self._clazz = clazz

    @property
    def type_name(self) -> str:
        return self._type_name

    @classmethod
    def from_name(cls, name: str) -> Optional["ArkValueType"]:
        return _ARK_VALUE_TYPE_LOOKUP.get(name)

    def get_property_type(self) -> Type[Any]:
        return self._clazz


# Module-level lookup cache for O(1) from_name lookups (built once at import time)
_ARK_VALUE_TYPE_LOOKUP = {item._type_name: item for item in ArkValueType}
    

def get_bytes_for_value(value_type: ArkValueType, value: Any) -> bytes:
    if value_type == ArkValueType.Boolean:
        return b"\x01" if value else b"\x00"
    elif value_type == ArkValueType.Byte:
        return value.to_bytes(1, byteorder="little")
    elif value_type == ArkValueType.Float:
        import struct
        return struct.pack('<f', value)
    elif value_type == ArkValueType.Int:
        return value.to_bytes(4, byteorder="little", signed=True)
    elif value_type == ArkValueType.Enum:
        return value.value.to_bytes(1, byteorder="little")
    elif value_type == ArkValueType.Name:
        encoded = value.encode('utf-8')
        length = len(encoded)
        return length.to_bytes(4, byteorder="little") + encoded
    elif value_type == ArkValueType.Object:
        encoded = value.encode('utf-8')
        length = len(encoded)
        return length.to_bytes(4, byteorder="little") + encoded
    elif value_type == ArkValueType.String:
        encoded = value.encode('utf-8')
        length = len(encoded)
        return length.to_bytes(4, byteorder="little") + encoded
    elif value_type == ArkValueType.Double:
        import struct
        return struct.pack('<d', value)
    elif value_type == ArkValueType.Int16:
        return value.to_bytes(2, byteorder="little", signed=True)
    elif value_type == ArkValueType.Int64:
        return value.to_bytes(8, byteorder="little", signed=True)
    elif value_type == ArkValueType.Int8:
        return value.to_bytes(1, byteorder="little", signed=True)
    elif value_type == ArkValueType.UInt16:
        return value.to_bytes(2, byteorder="little", signed=False)
    elif value_type == ArkValueType.UInt32:
        return value.to_bytes(4, byteorder="little", signed=False)
    elif value_type == ArkValueType.UInt64:
        return int(value).to_bytes(8, byteorder="little", signed=False)
    elif value_type == ArkValueType.SoftObject:
        encoded = value.encode('utf-8')
        length = len(encoded)
        return length.to_bytes(4, byteorder="little") + encoded
    else:
        raise NotImplementedError
