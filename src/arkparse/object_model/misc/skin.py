import json
from uuid import UUID

from arkparse import AsaSave
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.utils.json_utils import DefaultJsonEncoder


class Skin(InventoryItem):
    is_equipped: bool = False
    class_name: str = "Skin"

    def __init_props__(self):
        super().__init_props__()

        self.is_equipped = self.object.get_property_value("bEquippedItem", default=False)

    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)

    def __str__(self):
        return f" ShortName: {self.get_short_name()} - ClassName: {self.class_name} - UUID: {self.object.uuid.__str__()} - Equipped: {self.is_equipped if self.is_equipped is not None else 'Unknown'}"

    def to_json_obj(self, include_owner_inv_uuid=True):
        json_obj = super().to_json_obj()

        # Grab already set properties
        json_obj["UUID"] = self.object.uuid.__str__()
        json_obj["ShortName"] = self.get_short_name()
        json_obj["ClassName"] = self.class_name
        json_obj["ItemArchetype"] = self.object.blueprint
        json_obj["bEquippedItem"] = self.is_equipped

        if include_owner_inv_uuid and self.owner_inv_uuid is not None:
            json_obj["OwnerInventoryUUID"] = self.owner_inv_uuid.__str__()

        # Grab remaining properties if any
        if self.object.properties is not None and len(self.object.properties) > 0:
            for prop in self.object.properties:
                if prop is not None and \
                        prop.name is not None and \
                        len(prop.name) > 0 and \
                        "ItemArchetype" not in prop.name and \
                        "bEquippedItem" not in prop.name:
                    prop_value = self.object.get_property_value(prop.name)
                    json_obj[prop.name] = prop_value

        return json_obj

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None,
                          indent=4, cls=DefaultJsonEncoder)
