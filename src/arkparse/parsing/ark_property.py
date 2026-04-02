from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, TYPE_CHECKING
from contextlib import contextmanager

from arkparse.logging import ArkSaveLogger

from arkparse.parsing.struct.ark_color import ArkColor
from arkparse.parsing.struct.ark_int_point import ArkIntPoint
from arkparse.parsing.struct.ark_linear_color import ArkLinearColor
from arkparse.parsing.struct.ark_quat import ArkQuat
from arkparse.parsing.struct.ark_rotator import ArkRotator
from arkparse.parsing.struct.ark_vector import ArkVector
from arkparse.parsing.struct.ark_unique_net_id_repl import ArkUniqueNetIdRepl
from arkparse.parsing.struct.ark_vector_bool_pair import ArkVectorBoolPair
from arkparse.parsing.struct.ark_server_custom_folder import ArkServerCustomFolder
from arkparse.parsing.struct.ark_crafting_resource_requirement import ArkCraftingResourceRequirement
from arkparse.parsing.struct.ark_player_death_reason import ArkPlayerDeathReason
from arkparse.parsing.struct.ark_primal_saddle_structure import ArkPrimalSaddleStructure
from arkparse.parsing.struct.ark_gene_trait_struct import ArkGeneTraitStruct
from arkparse.parsing.struct.ark_gacha_resource_struct import ArkGachaResourceStruct
from arkparse.parsing.struct.ark_gigantoraptor_bonded_struct import ArkGigantoraptorBondedStruct
from arkparse.parsing.struct.ark_tracked_actor_id_category_pair_with_bool import (
    ArkTrackedActorIdCategoryPairWithBool,
)
from arkparse.parsing.struct.ark_tracked_actor_id_category_pair import ArkTrackedActorIdCategoryPair
from arkparse.parsing.struct.ark_my_persistent_buff_datas import ArkMyPersistentBuffDatas
from arkparse.parsing.struct.ark_item_net_id import ArkItemNetId
from arkparse.parsing.struct.object_reference import ObjectReference
from arkparse.parsing.struct.ark_struct_type import ArkStructType
from arkparse.parsing.struct.ark_dino_ancestor_entry import ArkDinoAncestorEntry
from arkparse.parsing.struct.ark_custom_item_data import ArkCustomItemData
from arkparse.parsing.struct.ark_painting_key_value import ArkPaintingKeyValue
from arkparse.parsing.struct.ark_dino_order_id import ArkDinoOrderID
from arkparse.parsing.struct.ark_tribe_alliance import ArkTribeAlliance
from arkparse.parsing.struct.ark_tribe_rank_group import ArkTribeRankGroup
from arkparse.parsing.struct.ark_milestone_tree_level_and_index import ArkMilestoneTreeLevelAndIndex
from arkparse.parsing.struct.ark_patrol_group_saved_data import ArkPatrolGroupSavedData

from arkparse.parsing.ark_property_container import ArkPropertyContainer
from arkparse.parsing.ark_set import ArkSet

from .ark_value_type import ArkValueType
from ..enums.ark_enum import ArkEnumValue

UNSUPPORTED_STRUCTS: List[str] = []

if TYPE_CHECKING:
    from arkparse.parsing.ark_binary_parser import ArkBinaryParser

T = TypeVar("T")

# -------------------------------------------------------------------------------------------------
# Logging helpers
# -------------------------------------------------------------------------------------------------

@contextmanager
def log_block(title: str):
    ArkSaveLogger.enter_struct(title)
    try:
        yield
    finally:
        ArkSaveLogger.exit_struct()


def log_property_read(key: str, vtype: ArkValueType, start_pos: int, data_size: int, value: Any, position: int) -> None:
    # Fast path: check cached boolean directly (no method call overhead)
    if not ArkSaveLogger._parser_log_enabled:
        return
    ArkSaveLogger.parser_log(
        f"[property read: key={key}; type={vtype}; bin_pos={start_pos}; bin_size={data_size}; value={value}; index_pos={position}]"
    )


# -------------------------------------------------------------------------------------------------
# Lookup tables
# -------------------------------------------------------------------------------------------------

# Map ArkStructType enum to constructors. Some need data_size, so we wrap with lambdas of (bb, ds)
_STRUCT_READERS: Dict[ArkStructType, Callable[["ArkBinaryParser", int], Any]] = {
    ArkStructType.Color: lambda bb, ds: ArkColor(bb),
    ArkStructType.LinearColor: lambda bb, ds: ArkLinearColor(bb),
    ArkStructType.Quat: lambda bb, ds: ArkQuat(bb),
    ArkStructType.Rotator: lambda bb, ds: ArkRotator(bb),
    ArkStructType.Vector: lambda bb, ds: ArkVector(bb),
    ArkStructType.UniqueNetIdRepl: lambda bb, ds: ArkUniqueNetIdRepl(bb),
    ArkStructType.VectorBoolPair: lambda bb, ds: ArkVectorBoolPair(bb),
    ArkStructType.ArkTrackedActorIdCategoryPairWithBool: lambda bb, ds: ArkTrackedActorIdCategoryPairWithBool(bb),
    ArkStructType.ArkTrackedActorIdCategoryPair: lambda bb, ds: ArkTrackedActorIdCategoryPair(bb),
    ArkStructType.MyPersistentBuffDatas: lambda bb, ds: ArkMyPersistentBuffDatas(bb, ds),
    ArkStructType.ItemNetId: lambda bb, ds: ArkItemNetId(bb),
    ArkStructType.ArkDinoAncestor: lambda bb, ds: ArkDinoAncestorEntry(bb),
    ArkStructType.ArkIntPoint: lambda bb, ds: ArkIntPoint(bb),
    ArkStructType.ArkCustomItemData: lambda bb, ds: ArkCustomItemData(bb),
    ArkStructType.ArkServerCustomFolder: lambda bb, ds: ArkServerCustomFolder(bb),
    ArkStructType.ArkCraftingResourceRequirement: lambda bb, ds: ArkCraftingResourceRequirement(bb),
    ArkStructType.ArkPlayerDeathReason: lambda bb, ds: ArkPlayerDeathReason(bb),
    ArkStructType.ArkPrimalSaddleStructure: lambda bb, ds: ArkPrimalSaddleStructure(bb),
    ArkStructType.ArkGeneTraitStruct: lambda bb, ds: ArkGeneTraitStruct(bb),
    ArkStructType.GachaResourceStruct: lambda bb, ds: ArkGachaResourceStruct(bb),
    ArkStructType.GigantoraptorBondedStruct: lambda bb, ds: ArkGigantoraptorBondedStruct(bb),
    ArkStructType.ArkPaintingKeyValue: lambda bb, ds: ArkPaintingKeyValue(bb),
    ArkStructType.ArkDinoOrderID: lambda bb, ds: ArkDinoOrderID(bb),
    ArkStructType.ArkTribeAlliance: lambda bb, ds: ArkTribeAlliance(bb),
    ArkStructType.ArkTribeRankGroup: lambda bb, ds: ArkTribeRankGroup(bb),
    ArkStructType.ArkMilestoneTreeLevelAndIndex: lambda bb, ds: ArkMilestoneTreeLevelAndIndex(bb),
    ArkStructType.ArkPatrolGroupSavedData: lambda bb, ds: ArkPatrolGroupSavedData(bb),
}

# Flags driving how a primitive value is read
class _Spec:
    __slots__ = ("needs_unknown", "needs_pos_flag", "reader")

    def __init__(self, needs_unknown: bool, needs_pos_flag: bool, reader: Callable[["ArkBinaryParser"], Any]):
        self.needs_unknown = needs_unknown
        self.needs_pos_flag = needs_pos_flag
        self.reader = reader


_SIMPLE_SPECS: Dict[ArkValueType, _Spec] = {
    ArkValueType.Boolean: _Spec(False, False, lambda bb: bb.read_byte() != 0),
    ArkValueType.Int: _Spec(True, False, lambda bb: bb.read_int()),
    ArkValueType.Double: _Spec(True, False, lambda bb: bb.read_double()),
    ArkValueType.UInt32: _Spec(True, False, lambda bb: bb.read_uint32()),
    ArkValueType.UInt64: _Spec(True, False, lambda bb: bb.read_uint64()),
    ArkValueType.Int64: _Spec(True, False, lambda bb: bb.read_int64()),
    ArkValueType.SoftObject: _Spec(True, False, lambda bb: ArkProperty.read_soft_object_property_value(bb)),

    ArkValueType.Name: _Spec(False, True, lambda bb: bb.read_name()),
    ArkValueType.Float: _Spec(False, True, lambda bb: bb.read_float()),
    ArkValueType.Int8: _Spec(False, True, lambda bb: bb.read_byte()),
    ArkValueType.Object: _Spec(False, True, lambda bb: ObjectReference(bb)),
    ArkValueType.UInt16: _Spec(False, True, lambda bb: bb.read_uint16()),
    ArkValueType.Int16: _Spec(False, True, lambda bb: bb.read_short()),
    ArkValueType.String: _Spec(False, True, lambda bb: bb.read_string()),
}

_LOGGABLE_COMPLEX = {ArkValueType.Struct, ArkValueType.Array, ArkValueType.Map, ArkValueType.Set}


# -------------------------------------------------------------------------------------------------
# Dataclass
# -------------------------------------------------------------------------------------------------
@dataclass
class ArkProperty:
    name: str
    type: str
    value: Any
    position: int = field(default=0)
    unknown_byte: Optional[int] = field(default=None, repr=False)

    nr_of_bytes: int = field(default=0, init=False)
    name_position: int = field(default=0, init=False)
    value_position: int = field(default=0, init=False)
    bytes: Optional[bytes] = field(default=None, init=False, repr=False)

    def __init__(self, name: str, type: str, position: int, unknown_byte: int, value: T):
        # Keep ctor to match the original signature/behavior
        self.name = name
        self.type = type
        self.position = position
        self.unknown_byte = unknown_byte
        self.value = value
        self.nr_of_bytes = 0
        self.name_position = 0
        self.value_position = 0
        self.bytes = None

    def to_json_obj(self):
        return { "name": self.name, "type": self.type, "value": self.value.__str__() }

    # ---------------------------------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------------------------------
    @staticmethod
    def read_property(byte_buffer: "ArkBinaryParser", in_array: bool = False) -> Optional["ArkProperty"]:
        name_position = byte_buffer.get_position()
        value_position = 0
        byte_buffer.save_context.generate_unknown = True

        key = byte_buffer.read_name()
        byte_buffer.save_context.generate_unknown = False

        if key is None or key == "None":
            ArkSaveLogger.parser_log("Exiting struct (None marker) (pos = " + str(byte_buffer.get_position()) + " (hex: " + hex(byte_buffer.get_position()) + "))")
            ArkSaveLogger.exit_struct()

            if byte_buffer.size() - byte_buffer.position >= 4 and byte_buffer.peek_int() == 0:
                byte_buffer.skip_bytes(4)
            return None

        value_type = byte_buffer.read_value_type_by_name()
        data_size = byte_buffer.read_int()
        position = byte_buffer.read_int()
        start_data_position = byte_buffer.get_position()

        if value_type in _LOGGABLE_COMPLEX:
            ArkSaveLogger.parser_log(
                f"[prop={key};  type={value_type}; bin_pos={start_data_position}; size={data_size}; index_pos={position}]"
            )

        # Dispatch simple/complex
        if value_type in _SIMPLE_SPECS:
            prop, value_position = ArkProperty._read_simple_property(key, value_type, position, byte_buffer)
        elif value_type == ArkValueType.Byte:
            prop, value_position = ArkProperty._read_byte_property(key, position, data_size, byte_buffer)
        elif value_type == ArkValueType.Struct:
            byte_buffer.set_position(byte_buffer.get_position() - 8)  # V14 fix
            nr_of_names = byte_buffer.read_uint32()
            struct_type = byte_buffer.read_name()
            val, value_position = ArkProperty.read_struct_property(byte_buffer, data_size, struct_type, in_array, nr_of_names=nr_of_names)
            prop = ArkProperty(key, value_type.name, position, 0, val)
        elif value_type == ArkValueType.Array:
            prop, value_position = ArkProperty.read_array_property(key, value_type.name, position, byte_buffer, data_size)
        elif value_type == ArkValueType.Map:
            byte_buffer.set_position(byte_buffer.get_position() - 4)
            prop = ArkProperty.read_map_property(key, value_type.name, position, byte_buffer, data_size)
        elif value_type == ArkValueType.Set:
            byte_buffer.set_position(byte_buffer.get_position() - 4)
            prop = ArkProperty.read_set_property(key, value_type.name, position, byte_buffer, data_size)
        else:
            print(
                f"Unsupported property type {value_type} with data size {data_size} at position {start_data_position}"
            )
            prop = None

        if value_type not in _LOGGABLE_COMPLEX and prop is not None:
            log_property_read(key, value_type, start_data_position, data_size, prop.value, position)

        if prop is not None:
            prop.nr_of_bytes = data_size
            prop.name_position = name_position
            prop.value_position = value_position
            prop.bytes = byte_buffer.byte_buffer[name_position:byte_buffer.get_position()]

        return prop

    # ---------------------------------------------------------------------------------------------
    # Simple/primitive readers
    # ---------------------------------------------------------------------------------------------
    @staticmethod
    def _read_simple_property(key: str, vtype: ArkValueType, position: int, bb: "ArkBinaryParser") -> Tuple["ArkProperty", int]:
        spec = _SIMPLE_SPECS[vtype]

        unknown = bb.read_byte() if spec.needs_unknown else 0
        meta_flag = unknown
        if spec.needs_pos_flag:
            is_pos = bb.read_byte() == 1
            position = bb.read_int() if is_pos else 0
            meta_flag = is_pos  # preserve original semantics of unknown_byte field for these types
        value_position = bb.get_position()
        value = spec.reader(bb)

        return ArkProperty(key, vtype.name, position, meta_flag, value), value_position

    @staticmethod
    def _read_byte_property(key: str, position: int, data_size: int, bb: "ArkBinaryParser") -> Tuple["ArkProperty", int]:
        pre_read_pos = bb.get_position()
        is_enum = data_size != 0  # original heuristic

        if not is_enum:
            is_position = bb.read_byte() == 1  # or data size??? preserved behavior
            position = bb.read_int() if is_position else 0
            value_position = bb.get_position()
            byte_val = bb.read_unsigned_byte()
            return ArkProperty(key, ArkValueType.Byte.name, position, 0, byte_val), value_position

        # Enum path
        bb.set_position(pre_read_pos - 4)
        enum_type = bb.read_name()  # unused but kept
        _size = bb.read_int()
        _enum_bp = bb.read_name()  # unused but kept
        bb.validate_uint32(0)
        _enum_byte_size = bb.read_byte()
        bb.validate_uint32(0)
        enum_name = bb.read_name()
        ArkSaveLogger.parser_log(f"[ENUM: key={key}; value={ArkEnumValue(enum_name)}; start_pos={pre_read_pos}]")
        value_position = bb.get_position()
        return ArkProperty(key, ArkValueType.Enum, position, data_size, ArkEnumValue(enum_name)), value_position

    # ---------------------------------------------------------------------------------------------
    # Map/Set/Array readers
    # ---------------------------------------------------------------------------------------------
    @staticmethod
    def read_map_property(key: str, value_type_name: str, position: int, bb: "ArkBinaryParser", data_size: int) -> "ArkProperty":
        ArkSaveLogger.parser_log(f"Reading map property {key} with value type {value_type_name} at position {position} with data size {data_size}")
        key_type = bb.read_value_type_by_name()
        struct_names = bb.read_uint32()
        map_name = "None"

        if key_type == ArkValueType.Struct:
            value_type = bb.read_name()
        else:
            value_type = bb.read_value_type_by_name()
            struct_names = bb.read_int()
            if struct_names > 0:
                map_name = bb.read_name()

        ArkSaveLogger.parser_log(f"Map key type: {key_type}, value type: {value_type}, struct names: {struct_names}, map name: {map_name}")

        data_size, position, read_pos, _ = ArkProperty.__read_struct_header(bb, 0, in_map=True, nr_of_struct_names=struct_names)
        start_of_data = bb.get_position() - 4
        is_end = bb.position + data_size >= bb.size()
        is_end_m4 = bb.position + data_size - 4 >= bb.size()

        if (not is_end and bb.peek_name(data_size) != "") and (bb.peek_name() != "" or (not is_end_m4 and bb.peek_name(data_size-4) != "")):
            ArkSaveLogger.parser_log(f"Restoring position to {start_of_data} for MapStruct")
            bb.set_position(bb.position - 4)

        ArkSaveLogger.parser_log(f"Current position after map header: {bb.get_position()}, data size: {data_size}, expected end: {start_of_data + data_size}, buffer size: {bb.size()}")

        map_items = bb.read_uint32()
        ArkSaveLogger.parser_log(f"Map has {map_items} items")

        if key_type == ArkValueType.Struct:
            ArkSaveLogger.warning_log( f"Map with key type {key_type} is currently not supported, skipping map prop")
            bb.set_position(start_of_data + data_size)
            return None
        

        entries: List[ArkProperty] = []
        for _ in range(map_items):
            if value_type == ArkValueType.Struct:
                entries.append(ArkProperty.read_struct_map(key_type, bb, map_name))
            else:
                if value_type in _SIMPLE_SPECS and key_type in _SIMPLE_SPECS:
                    map_key = ArkProperty.read_property_value(key_type, bb)
                    map_value = ArkProperty.read_property_value(value_type, bb)
                    entry = ArkProperty(f"{map_key}", value_type.name, 0, 0, map_value)
                    entries.append(entry)
                    ArkSaveLogger.parser_log(f"Map entry: {map_key} -> {map_value}")
                else:
                    ArkSaveLogger.error_log(f"Unsupported map value type {value_type} in map {key}")
                    raise RuntimeError(f"Unsupported map value type {value_type} in map {key}")

        ArkProperty._fixup_if_left(bb, start_of_data, data_size, "Map")

        prop = ArkProperty(key, value_type_name, position, 0, ArkPropertyContainer(entries))
        
        return prop

    @staticmethod
    def read_struct_map(key_type: ArkValueType, bb: "ArkBinaryParser", map_name: str) -> "ArkProperty":
        props: List[ArkProperty] = []
        key_name = ArkProperty.read_property_value(key_type, bb)
        with log_block(f"Map({key_name}:{map_name})"):
            while bb.has_more():
                p = ArkProperty.read_property(bb)
                if p is None:
                    break
                props.append(p)
        return ArkProperty(key_name, "MapProperty", 0, 0, ArkPropertyContainer(props))

    @staticmethod
    def read_set_property(key: str, value_type_name: str, position: int, bb: "ArkBinaryParser", data_size: int) -> "ArkProperty":
        value_type = bb.read_value_type_by_name()
        bb.validate_uint32(0)
        data_size = bb.read_int()
        bb.validate_byte(0)
        start_of_data = bb.get_position()
        bb.validate_uint32(0)
        count = bb.read_int()

        with log_block(f"Set({value_type})"):
            values = [ArkProperty.read_property_value(value_type, bb) for _ in range(count)]

        if start_of_data + data_size != bb.get_position():
            print("Set read incorrectly, bytes left to read, expected:", start_of_data + data_size - bb.get_position())

        ArkSaveLogger.parser_log(f"Read set property {key} with {count} values of type {value_type_name}")
        ArkSaveLogger.parser_log(f"Set values: {values}")

        prop = ArkProperty(key, value_type_name, position, 0, ArkSet(value_type, values))
    
        return prop

    @staticmethod
    def read_array_property(key: str, type_: str, position: int, bb: "ArkBinaryParser", data_size: int) -> Tuple["ArkProperty", int]:
        # V14 no position in array
        bb.set_position(bb.get_position() - 4)
        array_type = bb.read_name()
        array_items = data_size
        nr_of_struct_names = bb.read_int()
        array_length = None

        if array_type != "StructProperty":
            data_size = bb.read_uint32()
            end_of_struct = bb.read_byte()
            data_start_position = bb.get_position()
            array_length = bb.read_uint32()
        else:
            end_of_struct = 0  # not used, keep for signature
            data_start_position = 0

        start_values_pos = bb.get_position()

        if array_type == "StructProperty":
            array_content_type = bb.read_name()
            data_size, position, _, _ = ArkProperty.__read_struct_header(bb, position, in_array=True, nr_of_struct_names=nr_of_struct_names)
            data_start_position = bb.get_position() - 4

            is_end = bb.position + data_size - 4 > bb.size()
            if bb.peek_name() != "" or (not is_end and bb.peek_name(data_size-4) != ""):
                ArkSaveLogger.parser_log(f"Restoring position to {data_start_position} for StructProperty")
                bb.set_position(bb.position - 4)

            array_items = bb.read_uint32()

            # if array_content_type == "PrimalCharacterStatusValueModifier":
            #     ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.PARSER, True)

            with log_block(f"Arr({array_content_type})"):
                ArkSaveLogger.parser_log(
                    f"[STRUCT ARRAY: key='none'; nr_of_value={array_items}; type={array_content_type}; bin_length={data_size}]"
                )
                struct_array = [
                    ArkProperty.read_struct_property(bb, data_size, array_content_type, True)[0]
                    for _ in range(array_items)
                ]

            prop = ArkProperty(key, type_, position, 0, struct_array)
            if bb.position != data_start_position + data_size:
                ArkSaveLogger.warning_log(
                    f"Array read incorrectly, bytes left to read: {data_start_position + data_size - bb.position}, current position: {bb.position}"
                )
                ArkSaveLogger.warning_log(f"Skipping to the end of the struct, type: {array_content_type}")
                bb.set_position(data_start_position + data_size)
                bb.structured_print(to_default_file=True)
                ArkSaveLogger.open_hex_view(True)

            # if array_content_type == "PrimalCharacterStatusValueModifier":
            #     ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.PARSER, False)

            return prop, start_values_pos

        # Value array branch
        with log_block(f"Arr({array_type})"):
            ArkSaveLogger.parser_log(
                f"[VALUE ARRAY: key={key}; nr_of_values={array_length}; type={array_type}]"
            )

            if key == "MyPersistentBuffDatas":
                value, _ = ArkProperty.read_struct_property(bb, array_length, key, True)
                prop = ArkProperty(key, "Struct", position, 0x00, value)
            else:
                values: List[Any] = []
                for _ in range(array_length):
                    # Preserve original odd branch
                    if bb.read_uint32 == 0x09AD2622:  # pragma: no cover
                        values.append(bb.read_name())
                    else:
                        values.append(ArkProperty.read_property_value(ArkValueType.from_name(array_type), bb))

                if array_type != "ByteProperty":
                    for i, v in enumerate(values):
                        ArkSaveLogger.parser_log(f"value {i}: {v}")
                else:
                    ArkSaveLogger.parser_log(f"Array value: {values}")

                prop = ArkProperty(key, type_, position, end_of_struct, values)
                

        ArkSaveLogger.parser_log(f"============ END Arr({array_type}) ============")
        return prop, start_values_pos

    # ---------------------------------------------------------------------------------------------
    # Struct reading
    # ---------------------------------------------------------------------------------------------
    @staticmethod
    def __read_struct_header(bb: "ArkBinaryParser", position: int = 0, in_array: bool = False, in_map: bool = False, nr_of_struct_names: int = 1) -> Tuple[int, int, bool]:
        if nr_of_struct_names != 0:
            bb.validate_uint32(1)
        with log_block("StructHeader"):
            if nr_of_struct_names > 10:
                ArkSaveLogger.warning_log(f"Too many struct names: {nr_of_struct_names}; reverting to reading one name")
                nr_of_struct_names = 1
            ArkSaveLogger.parser_log(f"reading {nr_of_struct_names} names")
            for i in range(nr_of_struct_names):
                _new_name = bb.read_name()
                ArkSaveLogger.parser_log(f"name {i}: {_new_name}")
                bb.validate_uint32(0)
            data_size = bb.read_uint32()
            size_byte = bb.read_byte()  # V14 unknown byte

            no_pos_values = [0, 8]
            if in_array or in_map:
                no_pos_values = []

            read_pos = (size_byte not in no_pos_values)
            if read_pos:
                position = bb.read_uint32()

            ArkSaveLogger.parser_log(f"pos byte={size_byte}, pos read={read_pos}, position={position}, data size={data_size}")

        return data_size, position, read_pos, size_byte

    @staticmethod
    def read_struct_property(bb: "ArkBinaryParser", data_size: int, struct_type: str, in_array: bool, nr_of_names: int = 1) -> Any:
        if not in_array:
            with log_block(f"S({struct_type})"):            
                data_size, _, _, _ = ArkProperty.__read_struct_header(bb, nr_of_struct_names=nr_of_names)
                value_position = bb.get_position()
                return ArkProperty._read_struct_body(bb, data_size, struct_type, in_array), value_position
        else:
            ArkSaveLogger.parser_log(f"Reading struct property {struct_type} with data size {data_size}")
            value_position = bb.get_position()
            return ArkProperty._read_struct_body(bb, data_size, struct_type, in_array), value_position

    @staticmethod
    def _read_struct_body(bb: "ArkBinaryParser", data_size: int, struct_type: str, in_array: bool) -> Any:
        ark_struct_type = ArkStructType.from_type_name(struct_type)
        
        if (ark_struct_type is not None) or in_array:
            if in_array and bb.peek_name() == "None":
                ArkSaveLogger.parser_log("Exiting struct (None marker)")
                return bb.read_name()
            if data_size <= 4:
                ArkSaveLogger.parser_log(f"Reading struct {struct_type} as primitive value")
                return None
            if ark_struct_type in _STRUCT_READERS:
                ArkSaveLogger.parser_log(f"Reading struct {struct_type} with data size {data_size}")
                return _STRUCT_READERS[ark_struct_type](bb, data_size)
            if in_array:
                if struct_type not in UNSUPPORTED_STRUCTS:
                    ArkSaveLogger.warning_log(f"Unsupported struct type {struct_type} in array")
                    UNSUPPORTED_STRUCTS.append(struct_type)
                
                # uncomment the lines below if you want to make objects of unknown structs
                # ArkSaveLogger.parser_log(f"Reading struct {struct_type} as array")
                # bb.structured_print(to_default_file=True)
                # bb.store()
                # ArkSaveLogger.error_log(f"Unsupported struct type {struct_type} in array")
                # ArkSaveLogger.open_hex_view(True)
                # raise ValueError(f"Unsupported struct type {struct_type}")

        ArkSaveLogger.parser_log(f"Reading struct {struct_type} with data size {data_size} as property list at position {bb.get_position()}")
        # Fallback: struct as property list
        position = bb.get_position()
        props = ArkProperty.read_struct_properties(bb)
        if bb.get_position() != position + data_size and not in_array:
            ArkSaveLogger.warning_log(f"WARNING: Struct reading position mismatch for type {struct_type}")
            ArkSaveLogger.warning_log(
                f"StructType: {struct_type}, DataSize: {data_size}, Position: {position}, CurrentPosition: {bb.get_position()}"
            )
            bb.set_position(position + data_size)
        return props

    @staticmethod
    def read_struct_properties(bb: "ArkBinaryParser") -> ArkPropertyContainer:
        props: List[ArkProperty] = []
        struct_property = ArkProperty.read_property(bb)
        if struct_property is not None:
            ArkSaveLogger.parser_log(
                f"Struct properties: {struct_property.name} {struct_property.type} {struct_property.value}"
            )
        while struct_property:
            props.append(struct_property)
            if bb.has_more():
                struct_property = ArkProperty.read_property(bb)
                if struct_property is not None:
                    ArkSaveLogger.parser_log(
                        f"Struct properties: {struct_property.name} {struct_property.type} {struct_property.value}"
                    )
            else:
                break

        ArkSaveLogger.parser_log(f"Read {len(props)} struct properties")
        return ArkPropertyContainer(props)

    # ---------------------------------------------------------------------------------------------
    # Misc helpers
    # ---------------------------------------------------------------------------------------------
    @staticmethod
    def read_property_value(value_type: ArkValueType, bb: "ArkBinaryParser") -> Any:
        if value_type in _SIMPLE_SPECS:
            return _SIMPLE_SPECS[value_type].reader(bb)
        if value_type == ArkValueType.Byte:
            return bb.read_unsigned_byte()
        # if value_type == ArkValueType.Struct:
        #     prop, _ = ArkProperty.read_struct_property(bb, bb.read_int(), True)
        #     return prop
        raise RuntimeError(f"Cannot read value type: {value_type} at position {bb.get_position()}")

    @staticmethod
    def read_soft_object_property_value(bb: "ArkBinaryParser") -> str:
        with log_block("SfO"):
            names = []
            while bb.peek_int() != 0:
                obj_name = bb.read_name()
                names.append(obj_name)
            bb.validate_bytes_as_string("00 00 00 00", 4)
            ArkSaveLogger.parser_log(f"Read soft object property {names}")
            return names

    @staticmethod
    def _fixup_if_left(bb: "ArkBinaryParser", start: int, size: int, label: str) -> None:
        if bb.get_position() != start + size:
            remaining = bb.read_bytes(start + size - bb.get_position())
            ArkSaveLogger.parser_log(f"{label} read incorrectly, bytes left to read: {remaining}")

    def __str__(self):
        return f"ArkProperty(name={self.name}, type={self.type}, value={self.value})"
