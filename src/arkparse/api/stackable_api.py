from typing import Dict, List
from uuid import UUID

from arkparse.object_model.stackables import Resource, Ammo
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration

from .general_api import GeneralApi
class StackableApi(GeneralApi):
    class Classes:
        RESOURCE = Resource
        AMMO = Ammo

    _DEFAULT_CONFIG = GameObjectReaderConfiguration(
            blueprint_name_filter=lambda name: name is not None and ("Resources/PrimalItemResource" in name or "/PrimalItemConsumable" in name or "PrimalItemAmmo" in name)
    )

    @staticmethod
    def is_applicable_bp(blueprint: str) -> bool:
        return StackableApi._DEFAULT_CONFIG.blueprint_name_filter(blueprint)

    def __init__(self, save: AsaSave):
        config = StackableApi._DEFAULT_CONFIG
        super().__init__(save, config)
    
    def get_all(self, cls: "StackableApi.Classes", config = None, max_workers: int = 4) -> Dict[UUID, InventoryItem]:
        def is_valid(obj: ArkGameObject):
            is_bp = obj.get_property_value("bIsBlueprint")
            is_engram = obj.get_property_value("bIsEngram")
            return not (is_bp or is_engram)

        return super().get_all(cls, valid_filter=is_valid, config=config, max_workers=max_workers)
    
    def get_by_class(self, cls: "StackableApi.Classes", classes: List[str]) -> Dict[UUID, InventoryItem]:
        config = GameObjectReaderConfiguration(
            blueprint_name_filter=lambda name: name is not None and name in classes
        )

        return self.get_all(cls, config)
    
    def get_count(self, items: Dict[UUID, InventoryItem]) -> int:
        count = 0
        for item in items.values():
            count += item.quantity
        return count

    