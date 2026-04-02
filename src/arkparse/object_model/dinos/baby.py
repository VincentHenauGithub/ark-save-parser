from typing import Optional
from uuid import UUID
from enum import Enum

from arkparse.object_model.dinos.dino import Dino
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from .dino import Dino
from ...logging import ArkSaveLogger


class BabyStage(Enum):
    BABY = "Baby"
    JUVENILE = "Juvenile"
    ADOLESCENT = "Adolescent"

class Baby(Dino):
    percentage_matured: float = 0.0
    stage: BabyStage = BabyStage.BABY

    def __init_props__(self):
        super().__init_props__()

        self.percentage_matured = self.object.get_property_value("BabyAge", 0.0) * 100
        self.stage = self.__get_stage()
            
    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)

    def __get_stage(self) -> BabyStage:
        if self.percentage_matured < 10.0:
            return BabyStage.BABY
        elif self.percentage_matured < 50.0:
            return BabyStage.JUVENILE
        else:
            return BabyStage.ADOLESCENT
        
    def grow_up(self, percentage: float = 100.0):
        if percentage < 0 or percentage > 100:
            raise ValueError("Percentage must be between 0 and 100")
        self.percentage_matured = percentage
        self.stage = self.__get_stage()

        self.binary.replace_float(self.object.find_property("BabyAge"), percentage / 100.0)
        self.update_binary()

    @staticmethod
    def from_object(dino_obj: ArkGameObject, status_obj: ArkGameObject, baby: "Baby" = None):
        b: Baby = None
        if baby is not None:
            b = baby
            Dino.from_object(dino_obj, status_obj, b)
        elif dino_obj is not None:
            b = Baby()
            b.object = dino_obj
            b.__init_props__()
            Dino.from_object(dino_obj, status_obj, b)
        else:
            ArkSaveLogger.error_log(f"Cannot create Baby object from None.")

        return b
