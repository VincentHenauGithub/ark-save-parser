from typing import Optional
from uuid import UUID

from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from .baby import Baby
from .tamed_dino import TamedDino

class TamedBaby(TamedDino, Baby):

    def __init_props__(self):
        super().__init_props__()

    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)

    @staticmethod
    def from_object(dino_obj: ArkGameObject, status_obj: ArkGameObject):
        b: TamedBaby = TamedBaby()
        b.object = dino_obj
        b.__init_props__()

        TamedDino.from_object(dino_obj, status_obj, b)
        Baby.from_object(dino_obj, status_obj, b)

        return b
