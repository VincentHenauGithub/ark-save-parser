from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID
import random

from arkparse.parsing.struct.ark_rotator import ArkRotator
from arkparse.parsing.ark_property import ArkProperty
from arkparse.parsing.struct.actor_transform import ActorTransform

from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.parsing.ark_property_container import ArkPropertyContainer
from arkparse.saves.save_context import SaveContext
from arkparse.logging import ArkSaveLogger

class _NameMetadata:
    def __init__(self, name: str, offset: int, is_read_as_string: bool):
        self.name = name
        self.length = len(name)
        self.offset = offset
        self.is_read_as_string = is_read_as_string

@dataclass
class ArkGameObject(ArkPropertyContainer):
    uuid: Optional[UUID] = None
    uuid2: str = ""

    blueprint: Optional[str] = None
    location: Optional[ActorTransform] = None

    names: List[str] = field(default_factory=list)
    name_metadata: List[_NameMetadata] = field(default_factory=list)
    section: Optional[str] = None
    unknown: Optional[int] = None
    properties_offset : int = 0

    def __init__(self, uuid: Optional[UUID] = None, blueprint: Optional[str] = None, binary_reader: Optional[ArkBinaryParser] = None, from_custom_bytes: bool = False, no_header: bool = False):
        super().__init__()
        if binary_reader:
            ArkSaveLogger.set_file(binary_reader, "debug.bin")
            if not no_header:
                if not from_custom_bytes:
                    self.uuid = uuid
                    self.uuid2: UUID = None
                    binary_reader.set_position(0)

                    self.blueprint = binary_reader.read_name()

                    sContext : SaveContext = binary_reader.save_context
                    self.location = sContext.get_actor_transform(uuid) or None
                    ArkSaveLogger.debug_log(f"Retrieved actor location: {('Success' if self.location else 'Failed')}")
                    
                else:
                    self.uuid = binary_reader.read_uuid()
                    self.blueprint = binary_reader.read_string()

                ArkSaveLogger.debug_log(f"Blueprint: {blueprint}")
                binary_reader.validate_uint32(0)

            try:
                if not no_header:
                    offsets = []
                    if not from_custom_bytes:
                        nr_names = binary_reader.read_int()
                        self.names, offsets = binary_reader.read_names(nr_names)
                    else:
                        self.names = binary_reader.read_strings_array()

                    self.name_metadata = []
                    for i, offset in enumerate(offsets):
                        self.name_metadata.append(_NameMetadata(self.names[i], offset, binary_reader.save_context.is_read_names_as_strings()))

                    for name in self.names:
                        ArkSaveLogger.debug_log(f"Name: {name}")

                    self.section = binary_reader.read_part()
                    self.unknown = binary_reader.read_byte()

                    # Zero byte here, only in aberration???
                    is_zero = binary_reader.read_byte() == 0
                    if not is_zero:
                        binary_reader.set_position(binary_reader.position - 1)

                    ArkSaveLogger.debug_log(f"Section: {self.section}, Unknown: {self.unknown}")
                    
                    if from_custom_bytes:
                        binary_reader.validate_uint16(0)
                        binary_reader.validate_byte(0)
                        has_rotator = binary_reader.read_uint32() == 1
                        if has_rotator:
                            ArkRotator(binary_reader)  # Placeholder for rotation data

                        self.properties_offset = binary_reader.read_uint32()
                        binary_reader.validate_uint32(0)

                if not from_custom_bytes: 
                    self.read_properties(binary_reader, ArkProperty, binary_reader.size())
                    
                    if  binary_reader.size() - binary_reader.position >= 20:
                        binary_reader.set_position(binary_reader.size() - 20)
                        binary_reader.read_int()
                        self.uuid2 = binary_reader.read_uuid()

                        if binary_reader.has_more():
                            ArkSaveLogger.enable_debug = True
                            ArkSaveLogger.open_hex_view()
                            raise Exception("Unknown data left")
                        
                if no_header:
                    self.blueprint = self.get_property_value("ItemArchetype").value
            except Exception as e:
                print(f"Error while reading object {self.blueprint}:", e)
                raise e
    
    def __replace_name(self, new_class: str, binary: ArkBinaryParser):
        new_short_name = new_class.split(".")[-1] + "_"
        as_bytes = new_short_name.encode("utf-8")
        numbering = bytes([random.randint(49, 57) for _ in range(10)])
        new_bytes = as_bytes + numbering + b'\x00'

        if len(self.name_metadata) != 1:
            raise NotImplementedError("Renaming is only supported for objects with one name")
        
        md = self.name_metadata[0]
        prev_length = md.length + 1
        new_length = len(new_bytes)
        md.length = new_length - 1

        # replace length of name in name table
        binary.set_position(md.offset - 4)
        binary.replace_bytes(new_length.to_bytes(4, byteorder="little"))

        # replace name in name table
        binary.set_position(md.offset)
        binary.replace_bytes(new_bytes, nr_to_replace=prev_length)

    def change_class(self, new_class: str, binary: ArkBinaryParser):
        self.__replace_name(new_class, binary)
        self.blueprint = new_class

        # replace class id
        new_class_id = binary.save_context.get_name_id(new_class)

        if new_class_id is None:
            raise Exception(f"Class {new_class} not found in name table")

        binary.set_position(0)
        binary.replace_bytes(new_class_id.to_bytes(4, byteorder="little"))

    def re_number_names(self, binary: ArkBinaryParser, new_number: bytes = None):
        md = self.name_metadata[-1]
        ArkSaveLogger.set_file(binary, "debug.bin")
        new_bytes = bytes([random.randint(49, 57) for _ in range(10)]) if new_number is None else new_number

        if not md.is_read_as_string:
            raise NotImplementedError("Renumbering names is only supported for names read as strings")
        
        binary.set_position(md.offset + md.length - 11)
        underscore = 95
        binary.validate_byte(underscore)
        binary.replace_bytes(new_bytes, binary.position)
        md.name = md.name[:-11] + "_" + new_bytes.decode("utf-8")

        return binary.byte_buffer
    
    def get_name_number(self) -> bytes:
        md = self.name_metadata[-1]
        return md.name.split("_")[-1].encode("utf-8")
                    
    def read_props_at_offset(self, reader: ArkBinaryParser):
        reader.set_position(self.properties_offset)
        # if reader.position != self.properties_offset:
        #     ArkSaveLogger.open_hex_view()
        #     raise Exception("Invalid offset for properties: ", reader.position, "expected: ", self.properties_offset)
        self.read_properties(reader, ArkProperty, reader.size())
        # reader.read_int()
        # self.uuid2 = reader.read_uuid()

    def print_properties(self):
        print(f"Properties for {self.blueprint}:")
        super().print_properties()

    def read_double(self, reader: ArkBinaryParser, property_name: str) -> float:
        reader.validate_name(property_name)
        reader.validate_name("DoubleProperty")
        reader.validate_byte(0x08)
        reader.validate_uint64(0)
        value = reader.read_double()
        return value
    
    def read_boolean(self, reader: ArkBinaryParser, property_name: str) -> bool:
        reader.validate_name(property_name)
        reader.validate_name("BoolProperty")
        reader.validate_uint64(0)
        value = reader.read_boolean()
        return value
    
    def decode_name(self, buffer: ArkBinaryParser):
        buffer.validate_uint32(1)
        name = buffer.read_string()
        buffer.validate_uint32(0)
        return name