from dataclasses import dataclass
from uuid import UUID
from typing import Dict
from pathlib import Path

from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase
from arkparse.saves.asa_save import AsaSave
from arkparse.parsing.struct import get_uuid_reference_bytes
from arkparse.parsing import ArkBinaryParser

from .inventory_item import InventoryItem
# items array InventoryItems -> ArrayProperty -> ObjectProperty

@dataclass
class Inventory(ParsedObjectBase):
    items: Dict[UUID, InventoryItem]
    def __init__(self, uuid: UUID, binary: ArkBinaryParser, save: AsaSave = None):
        super().__init__(uuid, binary, save=save)
        self.items = {}

        item_arr = self.object.get_array_property_value("InventoryItems")
        for item in item_arr:
            item_uuid = UUID(item.value)
            item = InventoryItem(item_uuid, save=save)
            is_engram = item.object.get_property_value("bIsEngram")
            if is_engram is None or not is_engram:
                self.items[item_uuid] = item

    def add_item(self, item: UUID, save: AsaSave = None, store: bool = True):
        if len(self.items) == 0:
            raise ValueError("Currently, adding stuff to empty inventories is not supported!")
            # self.binary.set_property_position("bInitializedMe")
        else:
            self.object.find_property("InventoryItems")

        reader = ArkBinaryParser(save.get_game_obj_binary(item), save.save_context)
        self.items[item] = InventoryItem(item, reader)
        self.items[item].add_self_to_inventory(self.object.uuid)
        
        object_references = []
        for item in self.items.keys():
            object_references.append(get_uuid_reference_bytes(item))
        
        if len(self.items) == 0:
            raise ValueError("Currently, adding stuff to empty inventories is not supported!")
            # self.binary.insert_array("InventoryItems", "ObjectProperty", object_references)
        else:
            self.binary.set_property_position("InventoryItems")
            self.binary.replace_array("InventoryItems", "ObjectProperty", object_references)

        if save is not None and store:
            save.modify_game_obj(self.object.uuid, self.binary.byte_buffer)

        # from arkparse.logging import ArkSaveLogger
        # from arkparse.object_model import ArkGameObject
        # ArkSaveLogger.enable_debug = True
        # ArkSaveLogger.set_file(self.binary, "debug.bin")
        # obj = ArkGameObject(uuid='', blueprint='', binary_reader=self.binary)
        # ArkSaveLogger.open_hex_view(True)

    def remove_item(self, item: UUID, save: AsaSave = None):
        if len(self.items) == 0:
            return

        self.items.pop(item)
        self.binary.set_property_position("InventoryItems")
        
        object_references = []
        for item in self.items:
            object_references.append(get_uuid_reference_bytes(item))
        
        self.binary.replace_array("InventoryItems", "ObjectProperty", object_references if len(object_references) > 0 else None)

        if save is not None:
            save.modify_game_obj(self.object.uuid, self.binary.byte_buffer)

    def clear_items(self, save: AsaSave = None):
        if len(self.items) == 0:
            return
        
        self.items = []
        self.binary.set_property_position("InventoryItems")
        self.binary.replace_array("InventoryItems", "ObjectProperty", None)

        if save is not None:
            save.modify_game_obj(self.object.uuid, self.binary.byte_buffer)

    def store_binary(self, path: Path, name: str = None, prefix: str = "inv_", with_content: bool = True, no_suffix: bool = False):
        super().store_binary(path, name=name, prefix=prefix, no_suffix=no_suffix)
        if not with_content:
            return
        for key, item in self.items.items():
            item.store_binary(path, prefix="itm_")

    def __str__(self):
        out = f"Inventory(items={len(self.items)}; uuid={self.object.uuid})"
              
        for _, item in self.items.items():
            out += "\n   - " + item.get_short_name() + f" ({item.object.uuid})"

        return out
