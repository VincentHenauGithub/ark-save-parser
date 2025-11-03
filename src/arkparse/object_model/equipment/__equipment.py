import json
import math
from uuid import UUID
import os

from arkparse.logging import ArkSaveLogger
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.object_model.misc.object_crafter import ObjectCrafter
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.enums import ArkItemQuality, ArkEquipmentStat
from arkparse.saves.asa_save import AsaSave
from arkparse.utils.json_utils import DefaultJsonEncoder


class Equipment(InventoryItem):
    is_equipped: bool = False
    is_bp: bool = False
    crafter: ObjectCrafter = None
    rating: float = 1
    quality: int = ArkItemQuality.PRIMITIVE.value
    current_durability: float = 1.0
    class_name: str = "Equipment"

    def __init_props__(self):
        super().__init_props__()

        self.is_equipped = self.object.get_property_value("bEquippedItem", default=False)
        self.is_bp = self.object.get_property_value("bIsBlueprint", default=False)
        if not self.is_bp:
            self.crafter = ObjectCrafter(self.object)

        self.rating = self.object.get_property_value("ItemRating", default=1)
        self.quality = self.object.get_property_value("ItemQualityIndex", default=ArkItemQuality.PRIMITIVE.value)
        self.current_durability = self.object.get_property_value("SavedDurability", default=1.0)

    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)
            
    def get_internal_value(self, stat: ArkEquipmentStat) -> int:
        raise ValueError(f"Stat {stat} is not valid for {self.class_name}")
    
    def get_actual_value(self, stat: ArkEquipmentStat, internal_value: int) -> float:
        raise ValueError(f"Stat {stat} is not valid for {self.class_name}")
    
    def set_stat(self, stat: ArkEquipmentStat, value: float):
        raise ValueError(f"Stat {stat} is not valid for {self.class_name}")
    
    def generate_from_template(class_: str, save: AsaSave, is_bp: bool):
        raise ValueError("Cannot generate equipment from template for base class")
    
    def get_implemented_stats(self) -> list:
        raise ValueError("Cannot get implemented stats for base class") 
    
    def auto_rate(self, save: AsaSave = None):
        raise ValueError("Cannot auto rate for base class equipment")
    
    def get_average_stat(self, __stats = []) -> float:
        return sum(__stats) / len(__stats)

    def __determine_quality_index(self) -> int:
        if self.rating > 10:
            index = ArkItemQuality.ASCENDANT
        elif self.rating > 7:
            index = ArkItemQuality.MASTERCRAFT
        elif self.rating > 4.5:
            index = ArkItemQuality.JOURNEYMAN
        elif self.rating > 2.5:
            index = ArkItemQuality.APPRENTICE
        elif self.rating > 1.25:
            index = ArkItemQuality.RAMSHACKLE
        else:
            index = ArkItemQuality.PRIMITIVE

        return index
    
    def _auto_rate(self, multiplier: float, average_stat: int):
        self.rating = average_stat * multiplier
        self.quality = self.__determine_quality_index()
        self.set_quality_index(self.quality)
        self.set_rating(self.rating)

    def _get_stat_for_rating(self, stat: ArkEquipmentStat, _: float, __: float) -> float:
        raise ValueError(f"Stat {stat} is not valid for {self.class_name}")
    
    def get_stat_for_rating(self, _: ArkEquipmentStat, __: float) -> float:
        raise ValueError(f"Merthod get_stat_for_rating is not implemented for {self.class_name}")

    @staticmethod
    def _generate_from_template(own_class: callable, template_file: str, bp_class: str, save: AsaSave):
        uuid, _ = super()._generate(save, os.path.join("templates", "equipment", template_file))
        eq: "Equipment" = own_class(uuid, save)
        eq.binary.replace_bytes(uuid.bytes, position=len(eq.binary.byte_buffer) - 16)
        name_id = save.save_context.get_name_id(bp_class) # gnerate name id if needed
        if name_id is None:
            save.add_name_to_name_table(bp_class)
        eq.reidentify(uuid, bp_class)
        return eq

    def is_rated(self) -> bool:
        return self.rating != 1  

    def is_crafted(self) -> bool:
        return False if self.crafter is None else self.crafter.is_valid()

    def set_quality_index(self, quality: ArkItemQuality):
        if self.quality == ArkItemQuality.PRIMITIVE.value:
            raise ValueError("Cannot modify quality of an item with quality 0")
        
        self.quality = quality.value
        self.binary.replace_byte_property(self.object.find_property("ItemQualityIndex"), quality.value)
        self.update_binary()

    def set_rating(self, rating: int):
        if not self.is_rated():
            raise ValueError(f"Cannot modify rating of a default crafted item (rating={self.rating})")

        self.rating = rating
        self.binary.replace_float(self.object.find_property("ItemRating"), rating)
        self.update_binary()

    def set_current_durability(self, percentage: float):
        self.current_durability = percentage / 100
        self.binary.replace_float(self.object.find_property("SavedDurability"), self.current_durability)
        self.update_binary()

    def _set_internal_stat_value(self, value: float, position: ArkEquipmentStat) -> bool:
        prop = self.object.find_property("ItemStatValues", position.value)
        clipped = False

        if int(value) > 65535:
            ArkSaveLogger.warning_log(f"Value {value} for stat {position} is too high to fit in equipment value property, clipping to 65535")
            value = 65535
            clipped = True

        self.binary.replace_u16(prop, int(value))
        self.update_binary()

        return clipped

    def get_stat_value(self, position: ArkEquipmentStat) -> int:
        return self.object.get_property_value("ItemStatValues", position=position.value, default=0)
    
    def reidentify(self, new_uuid: UUID = None, new_class: str = None):
        super().reidentify(new_uuid)
        if new_class is not None:
            self.object.change_class(new_class, self.binary)
            uuid = self.object.uuid if new_uuid is None else new_uuid
            self.object = ArkGameObject(uuid=uuid, blueprint=new_class, binary_reader=self.binary)

    @staticmethod
    def from_inventory_item(item: InventoryItem, save: AsaSave, cls: callable = None):
        parser = ArkBinaryParser(item.binary.byte_buffer, save.save_context)
        if cls == None:
            cls = Equipment

        return cls(item.object.uuid, parser)
    
    def __str__(self):
        return f" BP: {self.is_bp} - Quality: {ArkItemQuality(self.quality).name} - Rating: {self.rating:.2f} - Crafted: {self.is_crafted()}"

    def to_json_obj(self):
        json_obj = super().to_json_obj()

        # Grab already set properties
        json_obj["ShortName"] = self.get_short_name(),
        json_obj["ClassName"] = self.class_name,
        json_obj["ItemArchetype"] = self.object.blueprint,
        json_obj["bIsBlueprint"] = self.is_bp
        json_obj["bEquippedItem"] = self.is_equipped
        json_obj["bIsRated"] = self.is_rated()
        json_obj["bIsCrafted"] = self.is_crafted()
        json_obj["ItemQualityIndex"] = self.quality
        json_obj["ItemRating"] = self.rating
        json_obj["SavedDurability"] = self.current_durability

        # Grab crafter if it exists
        if self.crafter is not None:
            json_obj["CrafterCharacterName"] = self.crafter.char_name
            json_obj["CrafterTribeName"] = self.crafter.tribe_name

        # Grab remaining properties if any
        if self.object.properties is not None and len(self.object.properties) > 0:
            for prop in self.object.properties:
                if prop is not None and \
                        prop.name is not None and \
                        len(prop.name) > 0 and \
                        "ItemArchetype" not in prop.name and \
                        "bIsBlueprint" not in prop.name and \
                        "bEquippedItem" not in prop.name and \
                        "ItemQualityIndex" not in prop.name and \
                        "ItemRating" not in prop.name and \
                        "SavedDurability" not in prop.name and \
                        "CrafterCharacterName" not in prop.name and \
                        "CrafterTribeName" not in prop.name and \
                        "ItemQuantity" not in prop.name and \
                        "ItemID" not in prop.name and \
                        "OwnerInventory" not in prop.name and \
                        "CustomItemDatas" not in prop.name:
                    prop_value = self.object.get_property_value(prop.name)
                    if "NextSpoilingTime" in prop.name or "SavedDurability" in prop.name:
                        if math.isnan(prop.value) or math.isinf(prop.value):
                            prop_value = None
                    json_obj[prop.name] = prop_value

        return json_obj

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
