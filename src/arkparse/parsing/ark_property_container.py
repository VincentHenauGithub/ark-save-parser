from typing import List, Optional, Type, TypeVar, Dict, TYPE_CHECKING
from dataclasses import dataclass, field

# Import ArkProperty only for type checking to avoid circular import
if TYPE_CHECKING:
    from arkparse.parsing.ark_property import ArkProperty
    from arkparse.parsing import ArkBinaryParser 

from arkparse.logging import ArkSaveLogger

T = TypeVar('T')
PRINT_DEPTH = 0

def set_print_depth(depth: int) -> None:
    global PRINT_DEPTH
    PRINT_DEPTH = depth

@dataclass
class ArkPropertyContainer:
    properties: List['ArkProperty'] = field(default_factory=list)
    # Property name index for O(1) lookups - only built for large containers
    _prop_index: Optional[Dict[str, List['ArkProperty']]] = field(default=None, repr=False)
    # List of properties that have nested containers (avoids isinstance checks)
    _nested_containers: Optional[List['ArkProperty']] = field(default=None, repr=False)

    def _build_index(self) -> None:
        """Build property name index for fast lookups (only if >= 5 properties)."""
        if len(self.properties) >= 5:  # Only worth it for containers with many properties
            self._prop_index = {}
            self._nested_containers = []
            for prop in self.properties:
                if prop.name not in self._prop_index:
                    self._prop_index[prop.name] = []
                self._prop_index[prop.name].append(prop)
                # Track properties with nested containers
                if isinstance(prop.value, ArkPropertyContainer):
                    self._nested_containers.append(prop)

    def read_properties(self, byte_buffer: "ArkBinaryParser", propertyClass: Type['ArkProperty'], next_object_index: int) -> None:
        last_property_position = byte_buffer.get_position()
        ArkSaveLogger.reset_struct_path()
        # ArkSaveLogger.open_hex_view(True)
        try:
            while byte_buffer.has_more() and byte_buffer.get_position() < next_object_index:
                last_property_position = byte_buffer.get_position()
                ark_property = propertyClass.read_property(byte_buffer)
                
                if ark_property is None:
                    # last property read and was None marker
                    break
                # else:
                #     ArkSaveLogger.parser_log(f"Base property read, binary index is {byte_buffer.get_position()} value is {ark_property.value}")

                self.properties.append(ark_property)

        except Exception as e:
            byte_buffer.set_position(last_property_position)
            ArkSaveLogger.error_log(f"Error reading properties at position {last_property_position} ({hex(last_property_position)}): {e}")
            # byte_buffer.find_names(type=2)
            raise e
        
        # Build index after reading all properties
        self._build_index()
        ArkSaveLogger.parser_log("Finished reading object properties")

    def print_properties(self):
        for property in self.properties:
            if isinstance(property.value, ArkPropertyContainer):
                property: ArkPropertyContainer
                property.value.print_properties()
            elif property.type == "Array":
                max_items = 10
                ArkSaveLogger.info_log(f"Array Property ({property.type}) ({property.position}): {property.name} = [")
                for i, item in enumerate(property.value):
                    if i >= max_items:
                        ArkSaveLogger.info_log(f"  ... and {len(property.value) - max_items} more items")
                        break
                    if isinstance(item, ArkPropertyContainer):
                        ArkSaveLogger.info_log(f"  [{i}]: {{")
                        item.print_properties()
                        ArkSaveLogger.info_log(f"  }}")
                    else:
                        ArkSaveLogger.info_log(f"  [{i}]: {item}")
                ArkSaveLogger.info_log("]")
            else:
                property: ArkProperty = property
                ArkSaveLogger.info_log(f"Property ({property.type}) ({property.position}): {property.name} = {property.value}")

    def has_property(self, name: str) -> bool:
        # Use index if available (post-read_properties), otherwise linear search
        if self._prop_index is not None:
            return name in self._prop_index
        return any(property.name == name for property in self.properties)

    def find_property(self, name: str, position: int = None) -> Optional['ArkProperty[T]']:
        # Fast path: use index if available
        if self._prop_index is not None:
            if name in self._prop_index:
                for prop in self._prop_index[name]:
                    if position is None or prop.position == position:
                        return prop
            # Only search nested containers if not found at top level
            # Use pre-computed list to avoid isinstance checks
            if self._nested_containers:
                for property in self._nested_containers:
                    sub_property = property.value.find_property(name, position)
                    if sub_property:
                        return sub_property
            return None
        
        # Fallback: linear search (for containers created without read_properties)
        for property in self.properties:
            if property.name == name and (position is None or property.position == position):
                return property
            elif isinstance(property.value, ArkPropertyContainer):
                sub_property = property.value.find_property(name, position)
                if sub_property:
                    return sub_property
        return None
    
    def find_all_properties_of_name(self, name: str) -> List['ArkProperty[T]']:
        # Use index if available
        if self._prop_index is not None:
            props = list(self._prop_index.get(name, []))
            # Also search nested containers using pre-computed list
            if self._nested_containers:
                for property in self._nested_containers:
                    sub_props = property.value.find_all_properties_of_name(name)
                    if sub_props:
                        props.extend(sub_props)
            return props
        
        # Fallback: linear search
        props = [prop for prop in self.properties if prop.name == name]
        for property in self.properties:
            if isinstance(property.value, ArkPropertyContainer):
                sub_props = property.value.find_all_properties_of_name(name)
                if sub_props:
                    props.extend(sub_props)

        return props

    def find_property_by_position(self, name: str, position: int) -> Optional['ArkProperty[T]']:
        # Use index if available
        if self._prop_index is not None and name in self._prop_index:
            for prop in self._prop_index[name]:
                if prop.position == position:
                    return prop
            return None
        
        # Fallback: linear search
        for property in self.properties:
            if property.name == name and property.position == position:
                return property
        return None
    
    def get_properties_before(self, name: str) -> List[str]:
        properties = []
        for property in self.properties:
            if property.name == name:
                break
            properties.append(property.name)
        return properties
    
    def get_properties_after(self, name: str) -> List[str]:
        properties = []
        found = False
        for property in self.properties:
            if found:
                properties.append(property.name)
            if property.name == name:
                found = True
        return properties

    def get_property_value(self, name: str, default = None, position: int = None) -> Optional[T]:
        property = self.find_property(name, position)
        return property.value if property else default

    def get_property_value_by_position(self, name: str, position: int, clazz: Type[T]) -> Optional[T]:
        property = self.find_property_by_position(name, position)
        return property.value if property else None

    def get_array_property_value(self, name: str, default = None) -> Optional[List[T]]:
        value = self.get_property_value(name, [])
        return value if isinstance(value, list) else default

    def get_properties(self) -> List['ArkProperty[T]']:
        return [f"{property.name}({property.type})" for property in self.properties]

    def get_properties_by_position(self, name: str, clazz: Type[T]) -> Dict[int, T]:
        return {property.position: property.value for property in self.get_properties(name, clazz)}
    
    @property
    def property_names(self) -> set[str]:
        props = set()
        for prop in self.properties:
            props.add(prop.name)

            if isinstance(prop.value, ArkPropertyContainer):
                props.update(prop.value.property_names)
        return props

    def to_json_obj(self):
        all_properties = []
        for ark_property in self.properties:
            all_properties.append(ark_property.to_json_obj())
        return { "properties": all_properties }

    def to_string(self, parent_indent: str = "", depth: int = 0) -> str:
        props_str = ""

        if PRINT_DEPTH > 0 and depth > PRINT_DEPTH:
            return f"{parent_indent}... (truncated at depth {PRINT_DEPTH})"
        
        for prop in self.properties:
            if isinstance(prop.value, ArkPropertyContainer):
                props_str += f"{parent_indent}{prop.name} ({prop.type}) (pos={prop.position}):\n"
                props_str += prop.value.to_string(parent_indent + "  ", depth=depth + 1) + "\n"
            elif prop.type == "Array":
                props_str += f"{parent_indent}{prop.name} ({prop.type}) (pos={prop.position}): ["
                ind = 0
                if len(prop.value) == 0:
                    props_str += "]\n"
                    continue
                else:
                    props_str += "\n"
                max_prints = 10
                prints = min(len(prop.value), max_prints)
                for item in prop.value[:prints]:
                    props_str += f"{parent_indent}  [{ind}]: "
                    ind += 1
                    if isinstance(item, ArkPropertyContainer):
                        props_str += item.to_string(parent_indent + "  ", depth=depth) + "\n"
                    else:
                        props_str += f"{str(item)}\n"
                if len(prop.value) > max_prints:
                    props_str += f"{parent_indent}  ... and {len(prop.value) - max_prints} more items\n"
                props_str += f"{parent_indent}]\n"
            else:
                props_str += f"{parent_indent}{str(prop)}\n"
        return props_str.rstrip()
