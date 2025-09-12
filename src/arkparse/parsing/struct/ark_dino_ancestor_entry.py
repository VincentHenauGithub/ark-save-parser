import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from arkparse.utils.json_utils import DefaultJsonEncoder


if TYPE_CHECKING:
    from arkparse.parsing import ArkBinaryParser
    from arkparse.object_model.dinos.dino_id import DinoId

class ArkDinoAncestor:
    name: str
    id_: "DinoId"

    def __init__(self, name: str, id1: int, id2: int):
        from arkparse.object_model.dinos.dino_id import DinoId
        self.name = name
        self.id_ = DinoId(id1, id2)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Ancestor:(name={self.name}, {self.id_})"
    
    def __eq__(self, other):
        if not isinstance(other, ArkDinoAncestor):
            return False
        return self.name == other.name and self.id_ == other.id_

    def to_json_obj(self):
        return { "name": self.name, "id1": self.id_.id1, "id2": self.id_.id2 }

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)

@dataclass
class ArkDinoAncestorEntry:
    male: ArkDinoAncestor
    female: ArkDinoAncestor

    def __init__(self, byte_buffer: "ArkBinaryParser"):
        male_name = byte_buffer.parse_string_property("MaleName")
        id1 = byte_buffer.parse_uint32_property("MaleDinoID1")
        id2 = byte_buffer.parse_uint32_property("MaleDinoID2")
        self.male = ArkDinoAncestor(male_name, id1, id2)

        female_name = byte_buffer.parse_string_property("FemaleName")
        id1 = byte_buffer.parse_uint32_property("FemaleDinoID1")
        id2 = byte_buffer.parse_uint32_property("FemaleDinoID2")
        self.female = ArkDinoAncestor(female_name, id1, id2)
        byte_buffer.validate_name("None")

    def __str__(self):
        return f"AncestorEntry:[M:{self.male}, F:{self.female}]"

    def to_json_obj(self):
        return { "male": self.male.to_json_obj(), "female": self.female.to_json_obj() }

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
    
    def __eq__(self, other):
        if not isinstance(other, ArkDinoAncestorEntry):
            return False
        return self.male == other.male and self.female == other.female
