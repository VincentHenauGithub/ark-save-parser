import struct
from typing import List
from uuid import UUID

from ._binary_reader_base import BinaryReaderBase
from arkparse.logging import ArkSaveLogger

# Try to import fast Rust implementation for read_name
try:
    from arkparse_fast import read_name_id_at as _read_name_id_at_fast
    _HAS_FAST_READ_NAME = True
except ImportError:
    _HAS_FAST_READ_NAME = False
    _read_name_id_at_fast = None

# Pre-compile struct formats for hot paths
_STRUCT_INT = struct.Struct('<i')
_STRUCT_UINT32 = struct.Struct('<I')
_STRUCT_NAME_PAIR = struct.Struct('<Ii')  # name_id (uint32) + always_zero (int32)

def _fast_uuid_from_bytes(b: bytes) -> UUID:
    """Create UUID from bytes, bypassing __init__ validation for speed."""
    # Directly set the 'int' slot, avoiding __init__ overhead
    # This is ~3-4x faster than UUID(bytes=b)
    u = object.__new__(UUID)
    object.__setattr__(u, 'int', int.from_bytes(b, 'big'))
    return u
    
class BaseValueParser(BinaryReaderBase):
    def __init__(self, data: bytes, save_context=None):
        super().__init__(data, save_context)

    def read_int(self) -> int:
        if self.position + 4 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read an int.")
        result = _STRUCT_INT.unpack_from(self.byte_buffer, self.position)[0]
        self.position += 4
        return result

    def read_uint32(self) -> int:
        if self.position + 4 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read an unsigned int.")
        result = _STRUCT_UINT32.unpack_from(self.byte_buffer, self.position)[0]
        self.position += 4
        return result

    def read_uint16(self) -> int:
        if self.position + 2 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read an unsigned short.")
        result = struct.unpack_from('<H', self.byte_buffer, self.position)[0]
        self.position += 2
        return result

    def read_uint64(self) -> int:
        if self.position + 8 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read an unsigned long.")
        result = struct.unpack_from('<Q', self.byte_buffer, self.position)[0]
        self.position += 8
        return result
    
    def read_int64(self) -> int:
        if self.position + 8 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read a long.")
        result = struct.unpack_from('<q', self.byte_buffer, self.position)[0]
        self.position += 8
        return result

    def read_bytes(self, count: int) -> bytes:
        if count > len(self.byte_buffer) - self.position:
            ArkSaveLogger.open_hex_view()
            raise ValueError("Attempting to read more bytes than available in the buffer: " + str(count) + " " + str(len(self.byte_buffer) - self.position))
        result = self.byte_buffer[self.position:self.position + count]
        self.position += count
        return result

    def skip_bytes(self, count: int):
        self.position += count

    def read_string(self) -> str:
       
        length = self.read_int()
        if length == 0:
            return None
        
        is_multi_byte = length < 0
        abs_length = abs(length)

        result = ""
        if is_multi_byte:
            ArkSaveLogger.parser_log(f"Reading multi-byte string of length {abs_length}")
            # ArkSaveLogger.open_hex_view(True)
            to_read: int = (abs_length * 2) - 2
            if to_read > 0:
                result = self.read_bytes(to_read).decode('utf_16_le', errors='ignore')
            terminator = self.read_uint16()  # Read the null terminator
        else:
            pre_read_pos = self.position
            result = self.read_bytes(abs_length - 1).decode('ascii', errors='ignore')
            terminator = self.read_byte()

        if terminator != 0:
            ArkSaveLogger.warning_log(f"Terminator is not zero: {terminator}")
            self.position = pre_read_pos
            # ArkSaveLogger.enable_debug = True
            ArkSaveLogger.open_hex_view()

        return result

    def read_chars(self, size: int) -> str:
        result = struct.unpack_from(f'<{size}s', self.byte_buffer, self.position)[0].decode('utf-16')
        self.position += size * 2
        return result

    def read_boolean(self) -> bool:
        return self.read_byte() != 0

    def read_float(self) -> float:
        if self.position + 4 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read a float.")
        result = struct.unpack_from('<f', self.byte_buffer, self.position)[0]
        self.position += 4
        return result

    def read_double(self) -> float:
        if self.position + 8 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read a double.")
        result = struct.unpack_from('<d', self.byte_buffer, self.position)[0]
        self.position += 8
        return result

    def read_short(self) -> int:
        if self.position + 2 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read a short.")
        result = struct.unpack_from('<h', self.byte_buffer, self.position)[0]
        self.position += 2
        return result

    def read_unsigned_byte(self) -> int:
        # ArkSaveLogger.enable_debug = True
        # ArkSaveLogger.set_file(self, "read_unsigned_byte")
        # ArkSaveLogger.open_hex_view(True)
        return self.read_byte() & 0xFF

    def read_byte(self) -> int:
        if self.position >= len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read a byte.")
        result = self.byte_buffer[self.position]
        self.position += 1
        return result

    def read_uuid(self) -> UUID:
        return _fast_uuid_from_bytes(self.read_bytes(16))
    
    def read_uuid_as_string(self) -> str:
        return str(self.read_uuid())

    def peek_int(self) -> int:
        current_position = self.position
        value = self.read_int()
        self.position = current_position
        return value

    def peek_byte(self) -> int:
        current_position = self.position
        value = self.read_byte()
        self.position = current_position
        return value
    
    def peek_u16(self) -> int:
        current_position = self.position
        value = self.read_uint16()
        self.position = current_position
        return value
    
    def peek_byte(self) -> int:
        current_position = self.position
        value = self.read_byte()
        self.position = current_position
        return value
    
    def peek_u16(self) -> int:
        current_position = self.position
        value = self.read_uint16()
        self.position = current_position
        return value
    
    def read_name(self, default=None, is_peek=False) -> str:
        if not self.save_context.has_name_table():
            return self.read_string()

        pos = self.position
        
        # Fast path: use Rust to read name_id and always_zero in one call
        if _HAS_FAST_READ_NAME and not is_peek:
            try:
                name_id, new_pos = _read_name_id_at_fast(self.byte_buffer, pos)
                name = self.save_context.get_name(name_id)
                
                if name is None:
                    if default is not None:
                        self.position = new_pos
                        return default
                    elif self.save_context.generate_unknown:
                        name = f"UnknownName_{name_id:08X}"
                        ArkSaveLogger.warning_log(f"Name with id {name_id} not found, generating unknown name: {name}")
                        self.position = new_pos
                        return name
                    else:
                        ArkSaveLogger.open_hex_view()
                        raise ValueError(f"Name is None, for name index {hex(name_id)} at position {pos}, generate_unknown is {self.save_context.generate_unknown}")
                
                # Handle NPCZoneVolume special case
                # NOTE: For NPCZoneVolume names, the "always_zero" field is actually the hex suffix,
                # NOT a zero. The Python fallback returns BEFORE reading always_zero.
                # So we must NOT use new_pos (which skips always_zero), but pos+4 instead.
                if "NPCZoneVolume" in name or "NPCCountVolume" in name:
                    self.position = pos + 4  # Only skip name_id, the next 4 bytes are the hex suffix
                    return name + "_" + hex(self.read_int())
                
                self.position = new_pos
                return name
            except (IndexError, ValueError):
                # Fall back to Python implementation on error
                pass
        
        # Original Python implementation (fallback or for is_peek)
        name_id = self.read_uint32()
        name = self.save_context.get_name(name_id)
        # print(f"Reading name with id {name_id} at position {self.position}, name: {name}")

        if is_peek:
            return name if name is not None else default

        if name is None and default is not None:
            name = default
            # print(f"Name with id {name_id} not found, using default: {name}")
            ArkSaveLogger.parser_log(f"Name with id {name_id} not found, using default: {name}")

        elif name is None and self.save_context.generate_unknown:
            name = f"UnknownName_{name_id:08X}"
            ArkSaveLogger.warning_log(f"Name with id {name_id} not found, generating unknown name: {name}")
        
        elif name is None:
            # ArkSaveLogger.enable_debug = True
            ArkSaveLogger.open_hex_view()
            raise ValueError(f"Name is None, for name index {hex(name_id)} at position {pos}, generate_unknown is {self.save_context.generate_unknown}")

        elif name == "NPCZoneVolume" or "NPCZoneVolume_" in name or "_NPCZoneVolume" in name or "NPCCountVolume" in name:
            return name + "_" + hex(self.read_int())

        always_zero = self.read_int()

        # no_prints = ["DontDoMaterialSpawning", "CorruptSpawnInValue", "LadderSocket", "Splus_SourceInclude", "Splus_SourceExclude"]
        # if always_zero != 0 and name not in no_prints:
        #     ArkSaveLogger.warning_log(f"Always zero is not zero: {always_zero}, for name {name} at position {pos}")
        
        return name
    
    def peek_name(self, ahead: int = 0) -> str:
        pos = self.position
        self.position += ahead
        name = self.read_name(default="", is_peek=True)
        self.position = pos
        return name
    
    def read_strings_array(self) -> List[str]:
        count = self.read_uint32()
        return [self.read_string() for _ in range(count)]

    def read_names(self, name_count: int) -> List[str]:
        names = []
        offsets = []

        for _ in range(name_count):
            if self.save_context.is_read_names_as_strings():
                offsets.append(self.position + 4)
                names.append(self.read_string())
            else:
                names.append(self.read_name())
        return names, offsets
    
    def read_bytes_as_hex(self, data_size: int) -> str:
        # Reads `data_size` bytes from the current position and returns them as a hexadecimal string
        bytes_data = self.read_bytes(data_size)
        return ' '.join(f"{byte:02X}" for byte in bytes_data)
    