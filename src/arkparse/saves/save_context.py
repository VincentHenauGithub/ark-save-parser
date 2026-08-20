from typing import Dict, List, Optional, TYPE_CHECKING
import threading
import uuid
from contextlib import contextmanager
from pathlib import Path
import random
import json

from arkparse.parsing.struct import ActorTransform
from .header_location import HeaderLocation
# from arkparse.object_model.npc_zone_volume import NpcZoneVolume

class SaveContext:
    def __init__(self):
        self.names: Dict[int, str] = {}
        self.constant_name_table: Optional[Dict[int, str]] = None
        self.some_other_table: Optional[Dict[int, str]] = None
        self.sections: List[HeaderLocation] = []
        self.actor_transforms: Dict[uuid.UUID, ActorTransform] = {}
        self.actor_transform_positions: Dict[uuid.UUID, int] = {}
        self.save_version: int = 0
        self.game_time: float = 0.0
        self.map_name: str = ""
        self.unknown_value: int = 0
        self.npc_zone_volumes: List["NpcZoneVolume"] = []
        self.all_uuids: List[uuid.UUID] = []
        # generate_unknown is per-thread (see the property below); one SaveContext
        # is shared by every worker thread of a parallel parse.
        self._local = threading.local()
        self.generate_unknown: bool = False
        self._has_name_table: bool = False  # Cached flag for fast lookup
        self.current_time = 0
        self.current_day = 0

    @property
    def generate_unknown(self) -> bool:
        """Whether name ids missing from the name table are fabricated instead of
        raising. Thread-local: on free-threaded builds `get_game_objects` parses
        with a ThreadPoolExecutor over this single shared context, so a plain
        attribute would let one thread switch it off while another is still
        inside a region that needs it on."""
        return getattr(self._local, "generate_unknown", False)

    @generate_unknown.setter
    def generate_unknown(self, value: bool) -> None:
        self._local.generate_unknown = bool(value)

    @contextmanager
    def unknown_names_allowed(self):
        """Fabricate unknown names for the duration of the block.

        Restores the previous value rather than forcing it off, so nested
        regions (a property read inside a CustomItemData, say) don't clobber
        the enclosing one, and an exception can't leak the flag on.
        """
        previous = self.generate_unknown
        self.generate_unknown = True
        try:
            yield
        finally:
            self.generate_unknown = previous

    def get_actor_transform(self, uuid_: uuid.UUID) -> Optional[ActorTransform]:
        return self.actor_transforms.get(uuid_)

    def has_name_table(self) -> bool:
        return self._has_name_table
    
    def set_names(self, names: Dict[int, str]) -> None:
        """Set the name table and update cached flag."""
        self.names = names
        self._has_name_table = bool(names) or self.constant_name_table is not None 

    def get_name(self, key: int) -> Optional[str]:
        if key in self.names:
            return self.names[key]
        elif self.constant_name_table and key in self.constant_name_table:
            return self.constant_name_table[key]
        elif self.generate_unknown:
            unknown_name = f"Unknown_{key}"
            self.names[key] = unknown_name
            return unknown_name
        return None

    def use_constant_name_table(self, constant_name_table: Dict[int, str]):
        self.constant_name_table = constant_name_table
        self._has_name_table = bool(self.names) or constant_name_table is not None

    def is_read_names_as_strings(self) -> bool:
        return self.save_version >= 13
    
    def store_names_to_json(self, path: Path):
        with open(path, "w") as f:
            json.dump(self.names, f, indent=4)

    def get_name_id(self, name: str) -> Optional[int]:
        for key, value in self.names.items():
            if value == name:
                return key
        
        return None

    def add_new_name(self, name: str, id: int = None) -> int:
        if id is not None:
            self.names[id] = name
            return id
    
        new_id = random.randint(0, int(2**31 - 1))
        while new_id in self.names:
            new_id = random.randint(0, int(2**31 - 1))
        self.names[new_id] = name
        
        return new_id