import json
from dataclasses import dataclass
from uuid import UUID
from typing import Dict
from pathlib import Path

from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase
from arkparse.saves.asa_save import AsaSave
from arkparse.parsing.struct import get_uuid_reference_bytes
from arkparse.logging import ArkSaveLogger

from .inventory_item import InventoryItem
from ...utils.json_utils import DefaultJsonEncoder


# items array InventoryItems -> ArrayProperty -> ObjectProperty

@dataclass
class Inventory(ParsedObjectBase):
    _items: Dict[UUID, InventoryItem]
    item_classes: Dict[UUID, str]
    started_empty: bool = False
    def __init__(self, uuid: UUID, save: AsaSave = None):
        super().__init__(uuid, save=save)
        self._items = {}
        self.item_classes = {}
        if self.object is None:
            ArkSaveLogger.error_log(f"Inventory object with UUID {uuid} could not be loaded from save, not found")
            return

        item_arr = self.object.get_array_property_value("InventoryItems")
        for item in item_arr:
            item_uuid = UUID(item.value)
            if self.save.is_in_db(item_uuid):
                item_class = self.save.get_class_of_uuid(item_uuid)
                self.item_classes[item_uuid] = item_class

    @property
    def items(self) -> Dict[UUID, InventoryItem]:
        if len(self._items) != len(self.item_classes):
            self._items = {}
            item_arr = self.object.get_array_property_value("InventoryItems")
            for item in item_arr:
                item_uuid = UUID(item.value)
                if item_uuid not in self._items.keys():
                    self._items[item_uuid] = InventoryItem(item_uuid, self.save)
        return self._items

    @property
    def number_of_items(self):
        return len(self.items)
    
    def get_items_of_class(self, class_name: str) -> Dict[UUID, InventoryItem]:
        result = {}
        for item_uuid, item_class in self.item_classes.items():
            if item_class == class_name:
                result[item_uuid] = self.get_item(item_uuid)
        return result
    
    def get_item(self, uuid: UUID) -> InventoryItem:
        if uuid in self.item_classes.keys():
            if uuid in self._items.keys():
                return self._items[uuid]
            else:
                item = InventoryItem(uuid, self.save)
                self._items[uuid] = item
                return item

    def add_item(self, item: UUID, store: bool = True):
        # An inventory holding nothing has no InventoryItems property at all --
        # ARK leaves out anything still at its class default -- so the first item
        # has to insert the array rather than replace it.
        was_empty = len(self.items) == 0

        self._items[item] = InventoryItem(item, self.save)
        self._items[item].add_self_to_inventory(self.object.uuid)
        self.item_classes[item] = self.save.get_class_of_uuid(item)

        object_references = [get_uuid_reference_bytes(i) for i in self._items.keys()]

        if was_empty:
            self.__insert_items_array(object_references)
        else:
            self.binary.set_property_position("InventoryItems")
            self.binary.replace_array("InventoryItems", "ObjectProperty", object_references)

        if store:
            self.update_binary()
        if was_empty:
            self.update_object()

    def __insert_items_array(self, object_references):
        """Give an empty inventory its InventoryItems array.

        Every inventory in a save that does carry items spells the array out
        directly before bInitializedMe, with the same two header values, so that
        is where and how it is written back.
        """
        for name in ("InventoryItems", "ObjectProperty"):
            if self.save.save_context.get_name_id(name) is None:
                self.save.add_name_to_name_table(name)

        position = self.binary.set_property_position("bInitializedMe")
        if position is None:
            raise ValueError(
                f"Inventory {self.object.uuid} has no bInitializedMe property to "
                "anchor its item list to")

        self.binary.insert_array("InventoryItems", "ObjectProperty", object_references,
                                 self.__ARRAY_HEADER, self.__ARRAY_TYPE_INT,
                                 position=position)

    # Constant across every InventoryItems array found in a save, whether it
    # holds one entry or a hundred.
    __ARRAY_HEADER = 1
    __ARRAY_TYPE_INT = 0

    @staticmethod
    def generate_from_template(save: AsaSave, class_: str) -> "Inventory":
        """Create an empty inventory of ``class_`` in ``save`` and return it.

        Items are added afterwards with :meth:`add_item`, which grows the empty
        layout into the populated one. The populated template is kept alongside
        it under ``assets/templates/inventory`` as the reference for that shape,
        but starting from it would mean carrying its item references along.
        """
        import os
        from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase

        uuid, _ = ParsedObjectBase._generate(save, os.path.join("templates", "inventory", "empty"))

        if save.save_context.get_name_id(class_) is None:
            save.add_name_to_name_table(class_)

        inventory = Inventory(uuid, save)
        inventory.reidentify(uuid, update=False)
        inventory.object.change_class(class_, inventory.binary)
        inventory.update_binary()
        inventory.update_object()
        return inventory

    def remove_item(self, item: UUID):
        if len(self.items) == 0:
            return

        if item in self._items:
            self._items.pop(item)
            self.item_classes.pop(item)
        self.binary.set_property_position("InventoryItems")

        object_references = []
        for item in self._items:
            object_references.append(get_uuid_reference_bytes(item))

        self.binary.replace_array("InventoryItems", "ObjectProperty", object_references if len(object_references) > 0 else None)
        self.update_binary()

    def clear_items(self):
        if len(self.items) == 0:
            return

        self._items = {}
        self.item_classes = {}
        self.binary.set_property_position("InventoryItems")
        self.binary.replace_array("InventoryItems", "ObjectProperty", None)

        self.update_binary()

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

    def to_json_obj(self):
        json_items = []
        for key, item in self.items.items():
            json_items.append(item.to_json_obj(include_owner_inv_uuid=False))
        return { "UUID": self.object.uuid.__str__(), "InventoryItems": json_items }

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
