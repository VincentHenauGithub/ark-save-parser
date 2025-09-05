from typing import Optional
from uuid import UUID

from arkparse.object_model import ArkGameObject
from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase
from arkparse.parsing import ArkBinaryParser
from arkparse.saves.asa_save import AsaSave


class DinoAiController(ParsedObjectBase):
    targeting_team: int

    def __init_props__(self):
        super().__init_props__()

        self.targeting_team = self.object.get_property_value("TargetingTeam", 0)
    
    def __init__(self, uuid: UUID = None, save: AsaSave = None, game_bin: Optional[ArkBinaryParser] = None, game_obj: Optional[ArkGameObject] = None):
        super().__init__(uuid, save=save, game_bin=game_bin, game_obj=game_obj)
