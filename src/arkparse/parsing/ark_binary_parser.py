from pathlib import Path
from typing import List, Dict, TYPE_CHECKING
from uuid import UUID
from io import BytesIO
import zlib

from arkparse.parsing.struct.actor_transform import ActorTransform
from arkparse.logging import ArkSaveLogger
from ._property_parser import PropertyParser
from ._property_replacer import PropertyReplacer
from .ark_value_type import ArkValueType
from collections import deque
from arkparse.utils.temp_files import TEMP_FILES_DIR

if TYPE_CHECKING:
    from arkparse import AsaSave

COMPRESSED_BYTES_NAME_CONSTANTS = {
        0: "TribeName",
        1: "StrProperty",
        2: "bServerInitializedDino",
        3: "BoolProperty",
        5: "FloatProperty",
        6: "ColorSetIndices",
        7: "ByteProperty",
        8: "None",
        9: "ColorSetNames",
        10: "NameProperty",
        11: "TamingTeamID",
        12: "ObjectProperty",
        13: "RequiredTameAffinity",
        14: "TamingTeamID",
        15: "IntProperty",
        16: "OwningPlayerID",
        17: "OwningPlayerName",
        19: "StructProperty",
        23: "DinoID1",
        24: "UInt32Property",
        26: "UntamedPoopTimeCache",
        25: "DinoID2",
        31: "UploadedFromServerName",
        32: "TamedOnServerName",
        34: "UnknownProperty", # !!!
        36: "TargetingTeam",
        38: "bReplicateGlobalStatusValues",
        39: "bAllowLevelUps",
        40: "bServerFirstInitialized",
        41: "ExperiencePoints",
        42: "CurrentStatusValues",
        44: "ArrayProperty",
        55: "bIsFemale",
        56: "UnknowColor1", # !!!
    }

class ArkBinaryParser(PropertyParser, PropertyReplacer):
    def __init__(self, data: bytes, save_context=None):
        super().__init__(data, save_context)

    @staticmethod
    def __wildcard_decompress(input_buffer):
        """
        Processes the input buffer using the wildcard inflation rules
        and returns the resulting decompressed buffer.

        :param input_buffer: The compressed input as bytes.
        :return: The decompressed output as bytes.
        """
        class ReadState:
            NONE = 0
            ESCAPE = 1
            SWITCH = 2

        fifo_queue = deque()
        output_buffer = bytearray()
        read_state = ReadState.NONE

        def read_from_input(data, pos):
            """Reads the next byte from the input buffer."""
            if pos < len(data):
                return data[pos], pos + 1
            return None, pos

        pos = 0
        while pos < len(input_buffer) or fifo_queue:
            if fifo_queue:
                output_buffer.append(fifo_queue.popleft())
                continue

            next_byte, pos = read_from_input(input_buffer, pos)
            if next_byte is None:
                print("End of stream")
                break

            if read_state == ReadState.SWITCH:
                return_value = 0xF0 | ((next_byte & 0xF0) >> 4)
                fifo_queue.append(0xF0 | (next_byte & 0x0F))
                output_buffer.append(return_value)
                read_state = ReadState.NONE
                continue

            if read_state == ReadState.NONE:
                if next_byte == 0xF0:
                    read_state = ReadState.ESCAPE
                    continue
                elif next_byte == 0xF1:
                    read_state = ReadState.SWITCH
                    continue
                elif 0xF2 <= next_byte < 0xFF:
                    # Insert padding bytes
                    byte_count = next_byte & 0x0F
                    fifo_queue.extend([0] * byte_count)
                    continue
                elif next_byte == 0xFF:
                    # Handle special FF case
                    b1, pos = read_from_input(input_buffer, pos)
                    b2, pos = read_from_input(input_buffer, pos)
                    if b1 is None or b2 is None:
                        raise ValueError("Unexpected end of stream after 0xFF")
                    fifo_queue.extend([0, 0, 0, b1, 0, 0, 0, b2, 0, 0, 0])
                    continue

            # Default case: append the byte to the output
            read_state = ReadState.NONE
            output_buffer.append(next_byte)

        return bytes(output_buffer)

    def __structured_print_print(self, msg: str, to_file: BytesIO, end: str = "\n"):
        if to_file is not None:
            to_file.write(msg.encode())
            to_file.write(end.encode())
        else:
            print(msg, end=end)

    def __structured_print_known(self, lengths: List[int], to_file: BytesIO = None):
        for length in lengths:
            if self.position >= len(self.byte_buffer):
                break
            
            for _ in range(length):
                if self.position >= len(self.byte_buffer):
                    break
                self.__structured_print_print(f"{self.read_byte():02x} ", to_file, end="")
            self.__structured_print_print("", to_file)
            self.__structured_print_print(f"{self.position}: ", to_file, end="")

    def __structured_print_string_property(self, to_file: BytesIO = None):
        self.validate_uint32(0)
        self.read_uint32()
        self.validate_byte(0)
        value = self.read_string()
        self.__structured_print_print(f"{value}", to_file)
        self.__structured_print_print(f"{self.position}: ", to_file, end="")

    def structured_print(self, to_file: BytesIO = None, to_default_file: bool = True):
        if to_default_file:
            file_path = TEMP_FILES_DIR / "structured_print.txt"
            to_file = file_path.open("wb")

        current_position = self.position
        known_structures = {
            "UInt32Property": [4,1,4,4],
            "DoubleProperty": [4,1,4,8],
            "IntProperty": [4,1,4,4],
            "ByteProperty": [4,1,4,1],
            "UInt16Property": [4,4,1,4,2],
        }
        names = self.find_names(no_print=True)
        self.position = 0
        printed = 0

        while self.has_more():
            if self.position >= len(self.byte_buffer):
                break
            
            in_names = self.position in names
            if in_names:
                self.set_position(self.position + 4)
                int_after = self.read_uint32()
                self.set_position(self.position - 8)
                in_names = int_after == 0
                if in_names:
                    if printed > 0:
                        self.__structured_print_print("", to_file)
                        self.__structured_print_print(f"{self.position}: ", to_file, end="")
                    name = names[self.position]
                    self.__structured_print_print(f"{name}", to_file)
                    self.set_position(self.position + 8)
                    self.__structured_print_print(f"{self.position}: ", to_file, end="")
                    printed = 0
                    if name in known_structures:
                        self.__structured_print_known(known_structures[name], to_file=to_file)
                        continue
                    elif name == "StrProperty":
                        self.__structured_print_string_property(to_file=to_file)
                        continue            
            if not in_names:
                self.__structured_print_print(f"{self.read_byte():02x} ", to_file, end="")
                printed += 1

                if printed == 4:
                    self.__structured_print_print("", to_file)
                    self.__structured_print_print(f"{self.position}: ", to_file, end="")
                    printed = 0  

        self.position = current_position
        self.__structured_print_print(" === End of structured print === ", to_file)

    @staticmethod
    def from_deflated_data(byte_arr: List[int]):
        parser = ArkBinaryParser(None)

        raw_data = BytesIO(bytes(byte_arr))
        header_data_bytes = raw_data.read(12)
        if len(header_data_bytes) < 12:
            raise ValueError("Insufficient data for header")
        
        header_parser = ArkBinaryParser(header_data_bytes)
        version = header_parser.read_uint32()
        if version < 0x0407:
            raise RuntimeError(f"Unsupported embedded data version (only Unreal 5.5 is supported), skipping")
        inflated_size = header_parser.read_uint32()
        names_offset = header_parser.read_uint32()

        compressed_data = raw_data.read()
        if not compressed_data:
            raise ValueError("No compressed data found")  

        # Decompress data with error handling
        try:
            decompressed = zlib.decompress(compressed_data) # decompress the data using the DEFLATE algorithm
        except zlib.error as e:
            raise RuntimeError(f"Failed to decompress data") from e
        
        if len(decompressed) != inflated_size:
            raise ValueError(f"Expected compressed size {inflated_size}, got {len(decompressed)}")

        parser.byte_buffer = ArkBinaryParser.__wildcard_decompress(decompressed)
        ArkSaveLogger.set_file(parser, "debug.bin")

        name_table = {}
        parser.position = names_offset

        name_count = parser.read_uint32()
        for i in range(name_count):
            name_table[i | 0x10000000] = parser.read_string()
        parser.save_context.names = name_table
        parser.save_context.constant_name_table = COMPRESSED_BYTES_NAME_CONSTANTS
        parser.position = 0

        return parser
    
    def read_value_type_by_name(self):
        position = self.get_position()
        key_type_name = self.read_name()
        key_type = ArkValueType.from_name(key_type_name)
        if key_type is None:
            # ArkSaveLogger.enable_debug = True
            ArkSaveLogger.open_hex_view()
            raise ValueError(f"Unknown value type {key_type_name} at position {position}")
        return key_type

    def read_actor_transforms(self) -> Dict[UUID, ActorTransform]:
        actor_transforms = {}
        actor_transform_positions = {}
        termination_uuid = UUID("00000000-0000-0000-0000-000000000000")
        position = self.get_position()
        uuid = self.read_uuid()

        while uuid != termination_uuid:
            actor_transforms[uuid] = ActorTransform(self)
            actor_transform_positions[uuid] = position
            uuid = self.read_uuid()

        return actor_transforms, actor_transform_positions
    
    def replace_name_ids(self, name_ids: Dict[int, str], save: "AsaSave" = None):
        # Update the template name encodings to the actal save name encodings
        for position, name in name_ids.items():
            name_id = self.save_context.get_name_id(name)
            if name_id is None:
                if save is not None:
                    save.add_name_to_name_table(name)
                    name_id = self.save_context.get_name_id(name)
            
            if name_id is None:
                raise ValueError(f"{self.save_context.get_name(self.read_uint32())}: Name {name} not found in save context, ensure it is present before generating object")
            self.replace_bytes(name_id.to_bytes(length=4, byteorder='little'), position=int(position))

            ArkSaveLogger.parser_log(f"Replaced name id at position {position} with {hex(name_id)} for name {name}")

    def read_part(self) -> str:
        part_index = self.read_int()
        if 0 <= part_index < len(self.save_context.sections):
            return self.save_context.sections[part_index]
        return None

    def read_uuids(self) -> List[UUID]:
        uuid_count = self.read_int()
        return [self.read_uuid() for _ in range(uuid_count)]
    
    def store(self, folder: Path, uuid: UUID):
        folder.mkdir(parents=True, exist_ok=True)
        with open(folder / f"{uuid}.bin", "wb") as f:
            f.write(self.byte_buffer)

    def find_names(self, no_print=False, type=0, use_id = False):
        if not self.save_context.has_name_table():
            return []
        
        original_position = self.get_position()
        max_prints = 150
        prints = 0

        if not no_print:
            ArkSaveLogger.parser_log("--- Looking for names ---")
        found = {}
        for i in range(self.size() - 4):
            self.set_position(i)
            int_value = self.read_uint32()
            name = self.save_context.get_name(int_value)
            
            if name is not None:
                found[int_value if use_id else i] = name
                self.set_position(i)
                if prints < max_prints:
                    if not no_print:
                        message = f"Found name: {name} at {self.read_bytes_as_hex(4)} (position {i})"
                        if type == 0:
                            ArkSaveLogger.parser_log(message)
                        elif type == 1:
                            ArkSaveLogger.warning_log(message)
                        elif type == 2:
                            ArkSaveLogger.error_log(message)
                    prints += 1
                i += 3  # Adjust index to avoid overlapping reads
        self.set_position(original_position)

        return found
        
    
    # def find_byte_sequence(self, bytes: bytes):
    #     original_position = self.get_position()
    #     max_prints = 75
    #     prints = 0

    #     ArkSaveLogger.parser_log("--- Looking for byte sequence ---")
    #     found = []
    #     for i in range(self.size() - len(bytes)):
    #         self.set_position(i)
    #         if self.read_bytes(len(bytes)) == bytes:
    #             found.append(i)
    #             self.set_position(i)
    #             if prints < max_prints:
    #                 ArkSaveLogger.parser_log(f"Found byte sequence at {self.read_bytes_as_hex(len(bytes))} (position {i})")
    #                 prints += 1
    #     self.set_position(original_position)
    #     return found

    def find_byte_sequence(self, pattern: bytes, adjust_offset: int = -1) -> List[int]:
        # adjust offset is a temporary fix for off-by-one errors which i still have to figure out
        original_position = self.get_position()
        max_prints = 20
        prints = 0
        found = []
        buffer = self.byte_buffer
        cur_offset = 0
        
        while True:
            pos = buffer.find(pattern)
            if pos == -1:
                break
            found.append(pos + cur_offset + adjust_offset)
            if prints < max_prints:
                ArkSaveLogger.parser_log(
                    f"Found byte sequence at {pos + cur_offset + adjust_offset}"
                )
                prints += 1
            buffer = buffer[pos + 1:]
            cur_offset += pos + 1
        
        self.set_position(original_position)
        return found

    
    
