from ..ark_game_object import ArkGameObject
from uuid import UUID
from arkparse.parsing import ArkBinaryParser
from arkparse.saves.asa_save import AsaSave

from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase
from arkparse.parsing.struct.object_reference import ObjectReference
from arkparse.parsing.struct.ark_item_net_id import ArkItemNetId
from arkparse.logging import ArkSaveLogger

class InventoryItem(ParsedObjectBase):
    binary: ArkBinaryParser
    object: ArkGameObject

    id_: ArkItemNetId
    owner_inv_uuid: UUID
    quantity: int

    def __init_props__(self):
        super().__init_props__()

        if self.object is not None:
            self.id_ = self.object.get_property_value("ItemID")
            self.quantity = self.object.get_property_value("ItemQuantity", default=1)
            owner_in: ObjectReference = self.object.get_property_value("OwnerInventory", default=ObjectReference())
            try:
                self.owner_inv_uuid = UUID(owner_in.value)
            except TypeError:
                ArkSaveLogger.error_log(f"Invalid UUID for OwnerInventory: {owner_in.value}")
                self.owner_inv_uuid = None
        else:
            ArkSaveLogger.warning_log("InventoryItem object is None, cannot initialize properties")

    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)

    def __str__(self):
        return f"InventoryItem(item={self.object.blueprint.split('/')[-1].split('.')[0]}, quantity={self.quantity})"
    
    def reidentify(self, new_uuid: UUID = None, new_class: str = None, update=True):
        self.id_.replace(self.binary)
        super().reidentify(new_uuid, update=False)
        if new_class is not None:
            self.object.change_class(new_class, self.binary)
            uuid = self.object.uuid if new_uuid is None else new_uuid
            self.object = ArkGameObject(uuid=uuid, blueprint=new_class, binary_reader=self.binary)

        if update:
            self.update_binary()

    def add_self_to_inventory(self, inv_uuid: UUID):
        old_id = self.owner_inv_uuid
        self.owner_inv_uuid = inv_uuid
        self.binary.byte_buffer = self.binary.byte_buffer.replace(old_id.bytes, inv_uuid.bytes)

    def to_string(self, name = "InventoryItem"):
        return f"{name}({self.get_short_name()}, quantity={self.quantity})"

    def set_quantity(self, quantity: int):
        self.quantity = quantity
        prop = self.object.find_property("ItemQuantity")
        self.binary.replace_u32(prop, quantity)

        self.update_binary()

    def get_inventory(self, save: AsaSave):
        if self.owner_inv_uuid is None:
            ArkSaveLogger.error_log(f"InventoryItem {self.object.uuid} has no owner inventory UUID")
            return None
        from .inventory import Inventory # placed here to avoid circular import
        return Inventory(self.owner_inv_uuid, save=save)
    
    # def get_owner(self, save: AsaSave):
    #     from .inventory import Inventory # placed here to avoid circular import
    #     inv: Inventory = self.get_inventory(save)
    #     return inv.
