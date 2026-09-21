from dataclasses import dataclass, field
from typing import List, Optional, Callable
from uuid import UUID
    


@dataclass
class GameObjectReaderConfiguration:
    uuid_filter: Optional[Callable[[UUID], bool]] = None
    blueprint_name_filter: Optional[Callable[[Optional[str]], bool]] = None
    property_names: List[str] = field(default_factory=list)
    selected_property_names: List[str] = field(default_factory=list)
