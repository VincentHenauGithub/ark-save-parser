from typing import Optional
from uuid import UUID
from pathlib import Path

from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.misc.inventory import Inventory
from arkparse.object_model import ArkGameObject

from .structure import Structure
from ...parsing import ArkBinaryParser


class StructureWithInventory(Structure):
    inventory_uuid: UUID
    item_count: int
    max_item_count: int

    _inventory: Inventory

    def __init__(self, uuid: UUID, save: AsaSave, bypass_inventory: bool = False, game_bin: Optional[ArkBinaryParser] = None, game_obj: Optional[ArkGameObject] = None):
        self._inventory = None
        super().__init__(uuid, save=save, game_bin=game_bin, game_obj=game_obj)
        self.save = save
        
        inv_uuid = self.object.get_property_value("MyInventoryComponent")
        self.inventory_uuid = UUID(inv_uuid.value) if inv_uuid is not None else None
        self.item_count = self.object.get_property_value("CurrentItemCount", default=0)
        self.max_item_count = self.object.get_property_value("MaxItemCount")

        if self.inventory_uuid is not None and not bypass_inventory:
            self._inventory = Inventory(self.inventory_uuid, save=self.save)

    @property
    def inventory(self) -> Inventory:
        if self._inventory is None and self.inventory_uuid is not None:
            self._inventory = Inventory(self.inventory_uuid, save=self.save)
        return self._inventory

    def set_item_quantity(self, quantity: int):
        if self.item_count != None:
            self.binary.replace_u32(self.object.find_property("CurrentItemCount"), quantity)
            self.item_count = quantity
            self.update_binary()

    def add_item(self, item: UUID):
        if self.item_count == self.max_item_count:
            return False
        
        if self.item_count == 0:
            raise ValueError("Currently, adding stuff to empty inventories is not supported!")
            
        self.set_item_quantity(self.item_count + 1)
        self.inventory.add_item(item)
        self.update_binary()
        return True
    
    def update_binary(self):
        if self.inventory is not None:
            self.inventory.update_binary()
        super().update_binary()

    def remove_item(self, item: UUID):
        if self.item_count == 0:
            return

        self.set_item_quantity(self.item_count - 1)
        self.inventory.remove_item(item)
        self.update_binary()
        self.save.remove_obj_from_db(item)

    def remove_from_save(self, save: AsaSave):
        for key, _ in self.inventory.items.items():
            save.remove_obj_from_db(key)
        save.remove_obj_from_db(self.inventory.object.uuid)
        super().remove_from_save(save)

    def clear_items(self):
        self.set_item_quantity(0)

        for item in self.inventory.items:
            self.save.remove_obj_from_db(item)

        self.inventory.clear_items()
        self.inventory.update_binary()

    def reidentify(self, new_uuid: UUID = None):
        super().reidentify(new_uuid)
        if self.inventory is not None:
            self.inventory.renumber_name(new_number=self.object.get_name_number())
        uuid = new_uuid if new_uuid is not None else self.object.uuid
        self.object = ArkGameObject(uuid=uuid, blueprint=self.object.blueprint, binary_reader=self.binary)

    def store_binary(self, path: Path, prefix: str = "str_"):
        super().store_binary(path, prefix=prefix)
        if self.inventory is None:
            print(f"Structure {self.object.uuid} (class={self.object.blueprint}) has no inventory")
        self.inventory.store_binary(path)
