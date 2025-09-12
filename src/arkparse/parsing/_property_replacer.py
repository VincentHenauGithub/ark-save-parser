from typing import TYPE_CHECKING

from ._property_insertor import PropertyInsertor
if TYPE_CHECKING:
    from arkparse.parsing.ark_property import ArkProperty
from arkparse.logging import ArkSaveLogger
from typing import Dict, List
import struct


class PropertyReplacer(PropertyInsertor):
    def __init__(self, data: bytes, save_context=None):
        super().__init__(data, save_context)

    def __check_property_alignment(self, property: "ArkProperty") -> int:
        if property.position != 0:
            return property.name_position # can't check alignment if the property is not the fist occurence
        
        actual_index = self.set_property_position(property.name)
        shift = actual_index - property.name_position
        if shift != 0:
            raise ValueError(f"Property {property.name} at {property.name_position} has unexpected shift {shift}, expected 0")
        return actual_index

    def set_property_position(self, property_name: str, occurrence_index: int = 0) -> int:
        if self.save_context is None:
            raise ValueError("Save context is not set")
        
        # print(f"Looking for property {property_name} at index {occurrence_index}")
        cur_pos = 0

        for i in range(self.size() - 4):
            self.set_position(i)
            int_value = self.read_uint32()
            if int_value not in self.save_context.names:
                continue
            name = self.save_context.names[int_value]
            if name is not None and name == property_name:
                # print("Reading pos at", self.position)
                # print(f"Found property: {name} at {self.position-8} (position {cur_pos})")
                if cur_pos == occurrence_index:
                    ArkSaveLogger.parser_log(f"Found property: {name} at {self.read_bytes_as_hex(4)} (position {i})")
                    self.set_position(i)
                    return i
                i += 16
                cur_pos += 1
        ArkSaveLogger.parser_log(f"Property {property_name} not found, returning position {self.position}")
        return None   

    def replace_string(self, property : "ArkProperty", value: str):
        # from arkparse.object_model.ark_game_object import ArkGameObject
        # ArkSaveLogger.enable_debug = True
        # ArkSaveLogger.set_file(self, "debug.bin")
        # obj = ArkGameObject(uuid='', blueprint='', binary_reader=self)
        # ArkSaveLogger.open_hex_view(True)

        self.__check_property_alignment(property)

        original_position = self.position
        new_length = len(value) + 1
        new_length_byte = (new_length + 4).to_bytes(1, byteorder="little")

        self.position = property.value_position - 5
        self.read_int() # full length
        self.validate_byte(0)
        current_string = self.read_string()
        current_nr_of_bytes = len(current_string) + 4

        # replace total length
        self.replace_bytes(new_length_byte, nr_to_replace=1, position=property.value_position - 5)

        # replace string
        lengthu32 = new_length.to_bytes(4, byteorder="little")
        self.replace_bytes(lengthu32 + value.encode("utf-8"), nr_to_replace=current_nr_of_bytes, position=property.value_position)

        self.set_position(original_position)
        # print(f"Replaced string {current_string} (length={current_nr_of_bytes}) at {property_position} with {value} at {string_pos}")

    def replace_u16(self, property : "ArkProperty", new_value: int):
        self.__check_property_alignment(property)
        new_value_bytes = new_value.to_bytes(2, byteorder="little")
        self.replace_bytes(new_value_bytes, position=property.value_position)
    
    def replace_16(self, property : "ArkProperty", new_value: int):
        self.__check_property_alignment(property)
        new_value_bytes = new_value.to_bytes(2, byteorder="little", signed=True)
        self.replace_bytes(new_value_bytes, position=property.value_position)

    def replace_u32(self, property : "ArkProperty", new_value: int):
        self.__check_property_alignment(property)
        new_value_bytes = new_value.to_bytes(4, byteorder="little")
        self.replace_bytes(new_value_bytes, position=property.value_position)

    def replace_u64(self, property : "ArkProperty", new_value: int):
        self.__check_property_alignment(property)
        new_value_bytes = new_value.to_bytes(8, byteorder="little")
        self.replace_bytes(new_value_bytes, position=property.value_position)

    def replace_float(self, property : "ArkProperty", new_value: float):
        self.__check_property_alignment(property)
        new_value_bytes = struct.pack('<f', new_value)
        self.replace_bytes(new_value_bytes, position=property.value_position)

    def replace_double(self, property : "ArkProperty", new_value: float):
        self.__check_property_alignment(property)
        new_value_bytes = struct.pack('<d', new_value)
        self.replace_bytes(new_value_bytes, position=property.value_position)
    
    def replace_boolean(self, property : "ArkProperty", new_value: bool):
        self.__check_property_alignment(property)
        new_value_bytes = b"\x01" if new_value else b"\x00"
        self.replace_bytes(new_value_bytes, position=property.value_position)

    def replace_byte_property(self, property : "ArkProperty", new_value: int):
        self.__check_property_alignment(property)
        new_value_bytes = new_value.to_bytes(1, byteorder="little")
        self.replace_bytes(new_value_bytes, position=property.value_position)

    def replace_struct_property(self, property: "ArkProperty", new_value: bytes):
        print(property)
        pos = self.__check_property_alignment(property)
        self.set_position(pos)
        self.validate_name(property.name)
        self.validate_name("StructProperty")
        self.validate_uint32(1)
        self.skip_bytes(8)  # skip struct type name
        self.validate_uint32(1)
        self.validate_name("/Script/CoreUObject")
        self.validate_uint32(0)
        data_length = self.read_uint32()

        if (self.position + 1 != property.value_position) and (self.position + 4 != property.value_position):
            raise ValueError(f"Invalid property alignment, expected position {self.position + 1} or {self.position + 4}, got {property.value_position}")
        if len(new_value) != data_length:
            raise ValueError(f"New value length {len(new_value)} does not match expected data length {data_length}")
        
        self.replace_bytes(new_value, position=property.value_position)

    def replace_array(self, array_name: str, property_type: str, new_items: List[bytes], position: int = None):
        if self.save_context is None:
            raise ValueError("Save context is not set")
        
        if position is not None:
            self.set_position(position)

        if property_type == "StructProperty":
            raise NotImplementedError("Replacing StructProperty arrays is not implemented yet")

        # remove array
        self.snip_bytes(8) # name
        self.snip_bytes(8) # ArrayProperty

        nr_of_items = self.read_uint32()
        self.set_position(self.position - 4)
        self.snip_bytes(4) # nr_of_items

        self.snip_bytes(8) # type name

        type_int = self.read_uint32()
        self.set_position(self.position - 4)
        self.snip_bytes(4) # type int

        array_length = self.read_uint32()
        self.set_position(self.position - 4)
        self.snip_bytes(4) # array length

        self.snip_bytes(1) # end of struct
        self.snip_bytes(array_length) # array itself

        # insert new array if needed
        if new_items is None:
            return
        

        self.insert_array(array_name, property_type, new_items, nr_of_items, type_int)
