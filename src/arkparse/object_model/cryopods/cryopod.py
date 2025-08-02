import logging
from uuid import UUID
from typing import List

from arkparse import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.object_model.equipment.saddle import Saddle
from arkparse.object_model.dinos.tamed_dino import TamedDino
from arkparse.parsing import ArkBinaryParser
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.parsing.struct.ark_custom_item_data import ArkCustomItemData

class EmbeddedCryopodData:
    class Item:
        DINO_AND_STATUS = 0
        SADDLE = 1
        COSTUME = 2
        HAT = 3
        GEAR = 4
        PET = 5

    custom_data: ArkCustomItemData
    
    def __init__(self, custom_item_data: ArkCustomItemData):
        self.custom_data = custom_item_data

    def __unembed__(self, item):
        parser = None
        try:
            if item == self.Item.DINO_AND_STATUS:
                bts = self.custom_data.byte_arrays[0].data if len(self.custom_data.byte_arrays) > 0 else b""
                if len(bts) != 0:
                    parser: ArkBinaryParser = ArkBinaryParser.from_deflated_data(bts)
                    parser.in_cryopod = True
                    
                    objects: List[ArkGameObject] = []
                    parser.skip_bytes(8)  # Skip the first 8 bytes (header)
                    nr_of_obj = parser.read_uint32()
                    parser.save_context.generate_unknown = True
                    for _ in range(nr_of_obj):
                        objects.append(ArkGameObject(binary_reader=parser, from_custom_bytes=True))
                    for obj in objects:
                        obj.read_props_at_offset(parser)
                    parser.save_context.generate_unknown = False
                        
                    return objects[0], objects[1]

                return None, None
            elif item == self.Item.SADDLE:
                bts = self.custom_data.byte_arrays[1].data if len(self.custom_data.byte_arrays) > 1 else b""
                if len(bts) != 0:
                    parser = ArkBinaryParser(bts)
                    parser.skip_bytes(4)  # Skip the first 8 bytes (header)
                    parser.validate_uint32(7)
                    parser.skip_bytes(8)  # Skip the first 8 bytes (header)
                    parser.save_context.generate_unknown = True
                    obj = ArkGameObject(binary_reader=parser, no_header=True)
                    parser.save_context.generate_unknown = False
                    
            else:
                logging.warning(f"Unsupported item type: {item}")
            
            return None
    
        except Exception as e:
            if "Unsupported embedded data version" not in str(e):
                logging.error(f"Error unembedding item {item}: {e}")
                parser.structured_print()
            raise e
    
    def get_dino_obj(self):
        return self.__unembed__(self.Item.DINO_AND_STATUS)
    
    def get_saddle_obj(self):
        return self.__unembed__(self.Item.SADDLE)

class Cryopod(InventoryItem): 
    embedded_data: EmbeddedCryopodData
    dino: TamedDino
    saddle: Saddle
    costume: any

    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)
        self.dino = None
        self.saddle = None
        self.costume = None
        custom_item_data = self.object.get_array_property_value("CustomItemDatas")
        self.embedded_data = EmbeddedCryopodData(custom_item_data[0]) if len(custom_item_data) > 0 else None

        if self.embedded_data is None:
            self.dino = None
            self.saddle = None
            return
        
        dino_obj, status_obj = self.embedded_data.get_dino_obj()
        
        if dino_obj is not None and status_obj is not None:
            self.dino = TamedDino.from_object(dino_obj, status_obj, self)
            self.dino.location.in_cryopod = True

        saddle_obj = self.embedded_data.get_saddle_obj()
        if saddle_obj is not None:
            self.saddle = Saddle.from_object(saddle_obj)  

    def is_empty(self):
        return self.dino is None 

    def __str__(self):
        if self.is_empty():
            return "Cryopod(empty)"
        
        return "Cryopod(dino={}, lv={}, saddle={})".format(self.dino.get_short_name(), self.dino.stats.current_level, "no saddle" if self.saddle is None else self.saddle.get_short_name())
