from dataclasses import dataclass
from typing import TYPE_CHECKING
from .object_reference import ObjectReference
from arkparse.logging import ArkSaveLogger
from .ark_key_value_pair import ArkKeyValuePair

if TYPE_CHECKING:   
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkByteArray:
    size: int
    data: bytes

    def __init__(self, ark_binary_data: "ArkBinaryParser"):
        ark_binary_data.validate_name("Bytes")
        ark_binary_data.validate_name("ArrayProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("ByteProperty")
        ark_binary_data.validate_uint32(0)

        ark_binary_data.read_uint32() # total size
        ark_binary_data.validate_byte(0)

        self.size = ark_binary_data.read_uint32()
        self.data = ark_binary_data.read_bytes(self.size) if self.size > 0 else b''

        ark_binary_data.validate_name("None")

    def to_json_obj(self):
        return { "size": self.size, "data": self.data.__str__() }

@dataclass
class ArkCustomItemData:
    byte_arrays: list[ArkByteArray] = None
    doubles: list[float] = None
    floats: list[float] = None
    strings: list[str] = None
    classes: list[ObjectReference] = None
    objects: list[ObjectReference] = None
    names: list[str] = None
    painting_id_map: list[ArkKeyValuePair] = None
    painting_revision_map: list[ArkKeyValuePair] = None
    custom_data_name: str = None
    custom_data_soft_classes: list[str] = None

    def __init__(self, ark_binary_data: "ArkBinaryParser"):
        total_size = self.__read_header(ark_binary_data)
        data_start = ark_binary_data.position
        ArkSaveLogger.parser_log(f"Reading CustomItemData at position {data_start}, expected size: {total_size} bytes")
        self.byte_arrays = []
        self._read_arrays(ark_binary_data)

        self.objects = []
        self.painting_id_map = []
        self.painting_revision_map = []
        self.custom_data_soft_classes = []

        self.doubles = self.__read_custom_data_doubles(ark_binary_data)
        self.strings = self.__read_custom_data_strings(ark_binary_data)
        self.floats = self._read_custom_data_floats(ark_binary_data)
        if ark_binary_data.peek_name() == "CustomDataObjects": # check if CustomDataObjects is present
            self.objects = self.__read_custom_data_objects(ark_binary_data)
        self.classes = self.__read_custom_data_classes(ark_binary_data)
        self.names = self.__read_custom_data_names(ark_binary_data)
        if ark_binary_data.peek_name() == "UniquePaintingIdMap":  # check if UniquePaintingIdMap is present
            self.painting_id_map = self.__read_painting_id_map(ark_binary_data)
        if ark_binary_data.peek_name() == "PaintingRevisionMap":  # check if PaintingRevisionMap is present
            self.painting_revision_map = self.__read_painting_revision_map(ark_binary_data)
        self.custom_data_name = self.__read_custom_data_name(ark_binary_data)
        if ark_binary_data.peek_name() == "CustomDataSoftClasses":  # check if CustomDataSoftClasses is present
            self.custom_data_soft_classes = self.__read_custom_data_soft_classes(ark_binary_data)

        ark_binary_data.validate_name("None")        

        ArkSaveLogger.parser_log(f"CustomItemData of type {self.custom_data_name} read successfully, total size: {total_size} bytes")
        for string in self.strings:
            ArkSaveLogger.parser_log(f"String: {string}")
        for obj in self.objects:
            ArkSaveLogger.parser_log(f"Object: {obj}")
        for double in self.doubles:
            ArkSaveLogger.parser_log(f"Double: {double}")
        for float_value in self.floats:
            ArkSaveLogger.parser_log(f"Float: {float_value}")
        for name in self.names:
            ArkSaveLogger.parser_log(f"Name: {name}")

    def to_json_obj(self, include_byte_arrays: bool = False):
        json_obj = { "doubles": self.doubles,
                     "floats": self.floats,
                     "strings": self.strings,
                     "classes": self.classes,
                     "objects": self.objects,
                     "painting_id_map": self.painting_id_map,
                     "painting_revision_map": self.painting_revision_map,
                     "custom_data_name": self.custom_data_name,
                     "custom_data_soft_classes": self.custom_data_soft_classes }

        if include_byte_arrays:
            json_obj["byte_arrays"] = self.byte_arrays

        return json_obj

    def __read_header(self, ark_binary_data: "ArkBinaryParser"):
        total_size = self.__read_struct_start(ark_binary_data, "CustomDataBytes", "CustomItemByteArrays")
        ArkSaveLogger.parser_log(f"CustomItemData total size: {total_size} bytes")

        return total_size
    
    def _read_arrays(self, ark_binary_data: "ArkBinaryParser"):
        arr_size, arr_start = self.__read_array_header(ark_binary_data)

        nr_of_arrays = ark_binary_data.read_uint32()
        self.nr_of_arrays = nr_of_arrays

        if nr_of_arrays == 0:
            ark_binary_data.validate_name("None")
            return

        for _ in range(nr_of_arrays):
            byte_array = ArkByteArray(ark_binary_data)
            if self.byte_arrays is None:
                self.byte_arrays = []
            self.byte_arrays.append(byte_array)

        if ark_binary_data.position != arr_start + arr_size:
            raise ValueError(f"Expected to read {arr_size} bytes, but read {ark_binary_data.position - arr_start} bytes")

        ark_binary_data.validate_name("None")
    
    def __read_array_header(self, ark_binary_data: "ArkBinaryParser"):
        ark_binary_data.validate_name("ByteArrays")
        ark_binary_data.validate_name("ArrayProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("StructProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("CustomItemByteArray")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("/Script/ShooterGame")
        ark_binary_data.validate_uint32(0)

        arr_size = ark_binary_data.read_uint32()
        ark_binary_data.validate_byte(0)
        arr_start = ark_binary_data.position

        return arr_size, arr_start
    
    def __read_custom_data_doubles(self, ark_binary_data: "ArkBinaryParser"):
        self.__read_struct_start(ark_binary_data, "CustomDataDoubles", "CustomItemDoubles")

        ark_binary_data.validate_name("Doubles")
        ark_binary_data.validate_name("ArrayProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("DoubleProperty")
        ark_binary_data.validate_uint32(0)
        ark_binary_data.read_uint32() # size of the data in bytes
        ark_binary_data.validate_byte(0)
        nr_of_values = ark_binary_data.read_uint32()

        doubles = [ark_binary_data.read_double() for _ in range(nr_of_values)]

        ark_binary_data.validate_name("None")

        return doubles
    
    def __read_custom_data_strings(self, ark_binary_data: "ArkBinaryParser"):
        ark_binary_data.validate_name("CustomDataStrings")
        ark_binary_data.validate_name("ArrayProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("StrProperty")
        ark_binary_data.validate_uint32(0)
        ark_binary_data.read_uint32() # size of the data in bytes
        ark_binary_data.validate_byte(0)
        nr_of_values = ark_binary_data.read_uint32()

        strings = [ark_binary_data.read_string() for _ in range(nr_of_values)]

        return strings

    def _read_custom_data_floats(self, ark_binary_data: "ArkBinaryParser"):
        ark_binary_data.validate_name("CustomDataFloats")
        ark_binary_data.validate_name("ArrayProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("FloatProperty")
        ark_binary_data.validate_uint32(0)
        ark_binary_data.read_uint32() # size of the data in bytes
        ark_binary_data.validate_byte(0)
        nr_of_values = ark_binary_data.read_uint32()

        floats = [ark_binary_data.read_float() for _ in range(nr_of_values)]

        return floats   
    
    def __read_custom_data_classes(self, ark_binary_data: "ArkBinaryParser"):
        ark_binary_data.validate_name("CustomDataClasses")
        ark_binary_data.validate_name("ArrayProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("ObjectProperty")
        ark_binary_data.validate_uint32(0)
        ark_binary_data.read_uint32() # size of the data in bytes
        ark_binary_data.validate_byte(0)
        
        nr_of_values = ark_binary_data.read_uint32()
        objects = []
        for _ in range(nr_of_values):
            obj = ObjectReference(ark_binary_data)
            objects.append(obj)

        return objects
    
    def __read_custom_data_objects(self, ark_binary_data: "ArkBinaryParser"):
        ark_binary_data.validate_name("CustomDataObjects")
        ark_binary_data.validate_name("ArrayProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("ObjectProperty")
        ark_binary_data.validate_uint32(0)
        ark_binary_data.read_uint32() # size of the data in bytes
        ark_binary_data.validate_byte(0)
        
        nr_of_values = ark_binary_data.read_uint32()
        objects = []
        for _ in range(nr_of_values):
            obj = ObjectReference(ark_binary_data)
            objects.append(obj)

        return objects
    
    def __read_custom_data_names(self, ark_binary_data: "ArkBinaryParser"):
        ark_binary_data.validate_name("CustomDataNames")
        ark_binary_data.validate_name("ArrayProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("NameProperty")
        ark_binary_data.validate_uint32(0)
        ark_binary_data.read_uint32() # size of the data in bytes
        ark_binary_data.validate_byte(0)
        nr_of_values = ark_binary_data.read_uint32()

        names = [ark_binary_data.read_name() for _ in range(nr_of_values)]

        return names
    
    def __read_painting_id_map(self, ark_binary_data: "ArkBinaryParser"):
        ark_binary_data.validate_name("UniquePaintingIdMap")
        ark_binary_data.validate_name("ArrayProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("StructProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("PaintingKeyValue")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("/Script/ShooterGame")
        ark_binary_data.validate_uint32(0)
        ark_binary_data.read_uint32() # size of the data in bytes
        ark_binary_data.validate_byte(0)
        nr_of_pairs = ark_binary_data.read_uint32()

        for _ in range(nr_of_pairs):
            pair = ArkKeyValuePair(ark_binary_data)
            if self.painting_id_map is None:
                self.painting_id_map = []
            self.painting_id_map.append(pair)

        if nr_of_pairs > 0:
            ark_binary_data.validate_name("None")
        
    def __read_painting_revision_map(self, ark_binary_data: "ArkBinaryParser"):
        ark_binary_data.validate_name("PaintingRevisionMap")
        ark_binary_data.validate_name("ArrayProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("StructProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("PaintingKeyValue")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("/Script/ShooterGame")
        ark_binary_data.validate_uint32(0)
        ark_binary_data.read_uint32()
        ark_binary_data.validate_byte(0)
        nr_of_pairs = ark_binary_data.read_uint32()

        for _ in range(nr_of_pairs):
            pair = ArkKeyValuePair(ark_binary_data)
            if self.painting_revision_map is None:
                self.painting_revision_map = []
            self.painting_revision_map.append(pair)

        if nr_of_pairs > 0:
            ark_binary_data.validate_name("None")
        
    def __read_custom_data_name(self, ark_binary_data: "ArkBinaryParser"):
        ark_binary_data.validate_name("CustomDataName")
        ark_binary_data.validate_name("NameProperty")
        ark_binary_data.validate_uint32(0)
        ark_binary_data.read_uint32()  # size of the data in bytes
        ark_binary_data.validate_byte(0)

        name = ark_binary_data.read_name()

        return name
    
    def __read_custom_data_soft_classes(self, ark_binary_data: "ArkBinaryParser"):
        ark_binary_data.validate_name("CustomDataSoftClasses")
        ark_binary_data.validate_name("ArrayProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("SoftObjectProperty")
        ark_binary_data.validate_uint32(0)
        ark_binary_data.read_uint32()
        ark_binary_data.validate_byte(0)

        nr_of_values = ark_binary_data.read_uint32()
        soft_classes = []

        for _ in range(nr_of_values):
            obj_name = ark_binary_data.read_name()
            ark_binary_data.validate_uint32(0)
            soft_classes.append(obj_name)

        return soft_classes

    def __read_struct_start(self, ark_binary_data: "ArkBinaryParser", name: str, content_type: str):
        ark_binary_data.validate_name(name)
        ark_binary_data.validate_name("StructProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name(content_type)
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("/Script/ShooterGame")
        ark_binary_data.validate_uint32(0)

        data_size = ark_binary_data.read_uint32()
        ark_binary_data.validate_byte(0)

        return data_size
    