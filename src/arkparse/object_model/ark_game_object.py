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

from arkparse.parsing._legacy_parsing.ark_property import ArkProperty as LegacyArkProperty
from arkparse.parsing._legacy_parsing.ark_binary_parser import ArkBinaryParser as LegacyArkBinaryParser

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
    parser_type: type = None

    def __init__(self, uuid: Optional[UUID] = None, blueprint: Optional[str] = None, binary_reader: Optional[ArkBinaryParser|LegacyArkBinaryParser] = None, from_custom_bytes: bool = False, no_header: bool = False):
        self.parser_type = ArkProperty if (isinstance(binary_reader, ArkBinaryParser) or binary_reader is None) else LegacyArkProperty
        self.uuid = uuid
        self.blueprint = blueprint
        string_name = False
        super().__init__()
        if binary_reader:
            ArkSaveLogger.set_file(binary_reader, "debug.bin")
            ArkSaveLogger.parser_log(f"Parsing object with UUID: {uuid}, Blueprint: {blueprint}, From custom bytes: {from_custom_bytes}, No header: {no_header}")
            if not no_header:
                if not from_custom_bytes:
                    self.uuid = uuid
                    self.uuid2: UUID = None
                    binary_reader.set_position(0)

                    self.blueprint, string_name = ArkGameObject.read_name(uuid, binary_reader)
                    ArkSaveLogger.parser_log(f"Read Blueprint: {self.blueprint} (String name: {string_name})")

                    sContext : SaveContext = binary_reader.save_context
                    self.location = sContext.get_actor_transform(uuid) or None
                    ArkSaveLogger.parser_log(f"Retrieved actor location: {('Success' if self.location else 'Failed')}")
                else:
                    self.uuid = binary_reader.read_uuid()
                    self.blueprint = binary_reader.read_string()
                    ArkSaveLogger.parser_log(f"Read UUID: {self.uuid}, Blueprint: {self.blueprint}")
                
                binary_reader.validate_uint32(0)
                if string_name:
                    binary_reader.read_uint16()

            try:
                if not (no_header or string_name):
                    ArkSaveLogger.parser_log(f"Reading names for object {self.blueprint} ({self.uuid})")
                    offsets = []
                    if not from_custom_bytes:
                        nr_names = binary_reader.read_int()
                        self.names, offsets = binary_reader.read_names(nr_names)
                    else:
                        self.names = binary_reader.read_strings_array()
                        ArkSaveLogger.parser_log(f"Read {len(self.names)} names from custom bytes")

                    self.name_metadata = []
                    for i, offset in enumerate(offsets):
                        self.name_metadata.append(_NameMetadata(self.names[i], offset, binary_reader.save_context.is_read_names_as_strings()))

                    for name in self.names:
                        ArkSaveLogger.parser_log(f"Name: {name}")

                    if "AnimSequence" in self.blueprint:
                        return

                    self.section = binary_reader.read_part()
                    self.unknown = binary_reader.read_short()

                    ArkSaveLogger.parser_log(f"Section: {self.section}, Unknown: {self.unknown}")
                    
                    if from_custom_bytes:
                        binary_reader.validate_uint16(0)
                        # binary_reader.validate_byte(0)
                        has_rotator = binary_reader.read_uint32() == 1
                        if has_rotator:
                            ArkRotator(binary_reader)  # Placeholder for rotation data

                        self.properties_offset = binary_reader.read_uint32()
                        ArkSaveLogger.parser_log(f"Properties offset: {self.properties_offset}")
                        binary_reader.validate_uint32(0)

                if not from_custom_bytes:
                    ArkSaveLogger.parser_log(f"Reading properties for object {self.blueprint} ({self.uuid})")
                    self.read_properties(binary_reader, self.parser_type, binary_reader.size())
                    
                    if  binary_reader.size() - binary_reader.position >= 20:
                        binary_reader.set_position(binary_reader.size() - 20)
                        binary_reader.read_int()
                        self.uuid2 = binary_reader.read_uuid()

                        if binary_reader.has_more():
                            # ArkSaveLogger.enable_debug = True
                            ArkSaveLogger.open_hex_view()
                            raise Exception("Unknown data left")
                        
                if no_header:
                    bp_ref = self.get_property_value("ItemArchetype", None)
                    if bp_ref is not None:
                        self.blueprint = bp_ref.value
            except Exception as e:
                ArkSaveLogger.error_log(f"Error while reading object {self.blueprint} ({self.uuid}): {e}")
                ArkSaveLogger.set_file(binary_reader, "debug.bin")
                raise e
    
    def __replace_name(self, new_class: str, binary: ArkBinaryParser):
        new_short_name = new_class.split(".")[-1] + "_"
        as_bytes = new_short_name.encode("utf-8")
        numbering = bytes([random.randint(49, 57) for _ in range(10)])
        new_bytes = as_bytes + numbering + b'\x00'

        md = None
        if len(self.name_metadata) != 1:
            # try to find renumberable name
            for md_ in reversed(self.name_metadata):
                if self.get_short_name() in md_.name:
                    md = md_
                    break
                if md_.name.split("_")[-1].isdigit() and md_.name.split("_")[-1] != "1":
                    ArkSaveLogger.warning_log(f"Using renumberable name for renaming: {md_.name} (selected from last names) bp={self.blueprint} ({self.uuid})")
                    for md__ in self.name_metadata:
                        ArkSaveLogger.warning_log(f" - Name: {md__.name}, Offset: {md__.offset}, Is read as string: {md__.is_read_as_string}")
                    md = md_
                    break

            if md is None:
                ArkSaveLogger.error_log(f"Cannot rename object {self.blueprint} ({self.uuid}): multiple names found")
                for md_ in self.name_metadata:
                    ArkSaveLogger.error_log(f" - Name: {md_.name}, Offset: {md_.offset}, Is read as string: {md_.is_read_as_string}")
                raise NotImplementedError("Renaming is only supported for objects with one name")
        else:
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

    def change_class(self, new_class: str, binary: ArkBinaryParser, renumber: bool = True):
        if renumber:
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
                    
    def read_props_at_offset(self, reader: ArkBinaryParser, legacy: bool = False):
        reader.set_position(self.properties_offset)
        # if reader.position != self.properties_offset:
        #     ArkSaveLogger.open_hex_view()
        #     raise Exception("Invalid offset for properties: ", reader.position, "expected: ", self.properties_offset)
        if not legacy:
            reader.validate_byte(0)
        
        self.read_properties(reader, self.parser_type, reader.size())
        # reader.read_int()
        # self.uuid2 = reader.read_uuid()

    def print_properties(self):
        ArkSaveLogger.info_log(f"Properties for {self.blueprint} ({self.uuid}):")
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
    
    @staticmethod
    def read_name(obj_uuid: UUID, reader: ArkBinaryParser) -> str:
        reader.set_position(0)
        string_name = False

        try:
            class_name = reader.read_name()
        except Exception as e:
            # Check for string name instead of name table reference, this sometimes happens since Lost Colony
            # To be ivestigated why this happens
            reader.set_position(0)
            try:
                unknow_id = reader.read_uint32()
                reader.validate_uint64(0)
                reader.validate_uint32(1)
                class_name = reader.read_string()
                # reader.validate_uint32(0)
                string_name = True
                ArkSaveLogger.parser_log(f"Object {obj_uuid} has string class name {class_name} instead of name table reference")
            except Exception as e:
                ArkSaveLogger.error_log(f"Error reading class name for object {obj_uuid}: {e}")
                reader.structured_print(to_default_file=True)
                input("Press Enter to continue...")
                class_name = "UnknownClass"
                
        return class_name, string_name
    
    def get_short_name(self) -> str:
        to_strip_end = [
            "_C",
            "_BP"
        ]

        to_strip_start = [
            "PrimalItemResource_",
            "PrimalItemAmmo_",
            "BP_"
        ]

        to_replace = {
            "_Character_BP": "",
            "_ASA_C": "",
            "StructureBP_": "",
            "PrimalItemStructure_": "",
            "PrimalItem_": "",
            "PrimalItem": "",
            "DinoCharacterStatus_BP": "Status",
        }

        short = self.blueprint.split('/')[-1].split('.')[0]

        for old, new in to_replace.items():
            short = short.replace(old, new)

        for strip in to_strip_end:
            if short.endswith(strip):
                short = short[:-len(strip)]

        for strip in to_strip_start:
            if short.startswith(strip):
                short = short[len(strip):]

        return short
    
    def __str__(self):
            return f"ArkGameObject(UUID: {self.uuid}, Blueprint: {self.blueprint}, Location: {self.location}, Properties: {len(self.properties)} properties)"