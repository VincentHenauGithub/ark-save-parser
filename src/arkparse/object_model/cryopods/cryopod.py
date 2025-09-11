import logging
from uuid import UUID
from typing import List, Optional

from arkparse import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.object_model.equipment.saddle import Saddle
from arkparse.object_model.dinos.tamed_dino import TamedDino
from arkparse.parsing import ArkBinaryParser
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.parsing.struct.ark_custom_item_data import ArkCustomItemData
from arkparse.logging import ArkSaveLogger
from arkparse.parsing.ark_property import ArkProperty

# legacy classes 
from arkparse.parsing._legacy_parsing.ark_binary_parser import ArkBinaryParser as LegacyArkBinaryParser
from arkparse.parsing._legacy_parsing.ark_property import ArkProperty as LegacyArkProperty

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
                    is_legacy = ArkBinaryParser.is_legacy_compressed_data(bts)
                    ArkSaveLogger.parser_log(f"Unembedding cryopod data, size: {len(bts)} bytes, legacy: {is_legacy}")
                    ParserClass: type[ArkBinaryParser] | type[LegacyArkBinaryParser] = LegacyArkBinaryParser if is_legacy else ArkBinaryParser
                    parser: ArkBinaryParser = ParserClass.from_deflated_data(bts)
                    parser.in_cryopod = True

                    try:
                        objects: List[ArkGameObject] = []
                        if not is_legacy:
                            parser.skip_bytes(8)  # Skip the first 8 bytes (header)
                        nr_of_obj = parser.read_uint32()
                        ArkSaveLogger.parser_log(f"Number of embedded objects: {nr_of_obj}")
                        parser.save_context.generate_unknown = True
                        for _ in range(nr_of_obj):
                            objects.append(ArkGameObject(binary_reader=parser, from_custom_bytes=True))
                        for obj in objects:
                            # parser.position += 8 if is_legacy else 0
                            obj.read_props_at_offset(parser, legacy=is_legacy)
                    except Exception as e:
                        ArkSaveLogger.error_log(f"Error reading embedded cryopod data:")
                        parser.structured_print()
                        ArkSaveLogger.parser_log(f"Made structured print of parser at error")
                        try:
                            ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.PARSER, True)
                            objects = []
                            parser.position = 4 if is_legacy else 12
                            for _ in range(nr_of_obj):
                                objects.append(ArkGameObject(binary_reader=parser, from_custom_bytes=True))
                            for obj in objects:
                                # parser.position += 8 if is_legacy else 0
                                obj.read_props_at_offset(parser, legacy=is_legacy)
                            ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.PARSER, False)
                        except Exception as _:
                            pass
                        raise e
                    parser.save_context.generate_unknown = False

                    if is_legacy:
                        ArkSaveLogger.parser_log("Parsed legacy cryopod data")
                        
                    return objects[0], objects[1]

                return None, None
            elif item == self.Item.SADDLE:
                bts = self.custom_data.byte_arrays[1].data if len(self.custom_data.byte_arrays) > 1 else b""
                if len(bts) != 0:
                    parser = ArkBinaryParser(bts)
                    first_int = parser.read_uint32()
                    if first_int > 6:
                        second_int = parser.read_uint32()
                        if second_int == 7:
                            parser.skip_bytes(8)
                            ArkSaveLogger.parser_log("Detected modern saddle data in cryopod")
                        else:
                            raise Exception("Unsupported embedded data version for saddle")
                    else:
                        parser = LegacyArkBinaryParser(bts)
                        PropType = LegacyArkProperty
                        parser.skip_bytes(4)
                        ArkSaveLogger.objects_log("Detected legacy saddle data in cryopod")
                    parser.save_context.generate_unknown = True
                    try:
                        obj = ArkGameObject(binary_reader=parser, no_header=True)
                    except Exception as e:
                        ArkSaveLogger.error_log(f"Error reading saddle data: {e}")
                        parser.structured_print()
                        parser.store()
                        ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.PARSER, True)
                        obj = ArkGameObject(binary_reader=parser, no_header=True)
                        ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.PARSER, False)
                        raise e
                    parser.save_context.generate_unknown = False
                    
            else:
                ArkSaveLogger.warning_log(f"Unsupported item type: {item}")
            
            return None
    
        except Exception as e:
            if "Unsupported embedded data version" not in str(e):
                ArkSaveLogger.error_log(f"Error unembedding item {item}: {e}")
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
        # ArkSaveLogger.debug_log(f"Parsing cryopod {uuid}")
        custom_item_data = self.object.get_array_property_value("CustomItemDatas")
        self.embedded_data = EmbeddedCryopodData(custom_item_data[0]) if len(custom_item_data) > 0 else None

        if self.embedded_data is None:
            self.dino = None
            self.saddle = None
            return
        
        dino_obj, status_obj = self.embedded_data.get_dino_obj()
        
        if dino_obj is not None and status_obj is not None:
            self.dino = TamedDino.from_object(dino_obj, status_obj, self)
            self.dino.save = save
            self.dino._location.in_cryopod = True

        saddle_obj = self.embedded_data.get_saddle_obj()
        if saddle_obj is not None:
            self.saddle = Saddle.from_object(saddle_obj)  
            self.saddle.save = save

    def is_empty(self):
        return self.dino is None 

    def __str__(self):
        if self.is_empty():
            return "Cryopod(empty)"
        
        return "Cryopod(dino={}, lv={}, saddle={})".format(self.dino.get_short_name(), self.dino.stats.current_level, "no saddle" if self.saddle is None else self.saddle.get_short_name())
