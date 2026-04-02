from uuid import UUID
from enum import Enum
from typing import List, Optional

from arkparse import AsaSave
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.object_model.equipment.saddle import Saddle
from arkparse.object_model.dinos.tamed_dino import TamedDino
from arkparse.parsing import ArkBinaryParser
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.parsing.struct.ark_custom_item_data import ArkCustomItemData
from arkparse.logging import ArkSaveLogger

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
                if len(bts) > 10:
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

                    props_to_purge = ['ItemQuantity', 'ItemStatValues', 'bAllowRemovalFromInventory', 'SteamUserItemID', 'CustomItemName', 'OriginalItemDropLocation', 'EggGenderOverride', 'ItemCustomClass', 'EggDinoAncestors', \
                                      'NextSpoilingTime', 'ClusterSpoilingTimeUTC', 'CustomItemDatas', 'EggNumberMutationsApplied', 'EggNumberOfLevelUpPointsApplied', 'bHideFromInventoryDisplay', 'CustomItemColors', 'CustomCosmeticAuthVars', \
                                      'CraftQueue', 'ExpirationTimeUTC', 'bIsBlueprint', 'bAllowRemovalFromSteamInventory', 'NextCraftCompletionTime', 'EggDinoGeneTraits', 'bFromSteamInventory', 'EggDinoAncestorsMale', 'bIsRepairing', \
                                      'EggColorSetIndices', 'ItemColorID', 'SlotIndex', 'bIsFoodRecipe', 'bIsInitialItem', 'OwnerPlayerDataId', 'LastSpoilingTime', 'CustomCosmeticModSkinVariantID', 'EggRandomMutationsFemale', \
                                      'ItemProfileVersion', 'PreSkinItemColorID', 'bIsCustomRecipe', 'AssociatedDinoID2', 'CustomCosmeticModSkinReplacementID', 'bIsFromAllClustersInventory', 'bDoApplyOriginalColorsWhenUnskinned', \
                                      'UploadEarliestValidTime', 'EggTamedIneffectivenessModifier', 'AssociatedDinoID1', 'WeaponClipAmmo', 'EggRandomMutationsMale']
                                      
                    new_props = []
                    for prop in obj.properties:
                        if prop.name not in props_to_purge:
                            new_props.append(prop)
                    obj.properties = new_props
                    obj.blueprint = obj.blueprint.replace("BlueprintGeneratedClass ", "")
                    
                    return obj
                return None 
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
    class CryopodType(Enum):
        NORMAL = "Normal"
        SCS = "SCS"
        PELAYORIS = "Pelayoris"
        DINO_DEPOT = "Dino Depot"
        
    embedded_data: EmbeddedCryopodData
    dino: TamedDino
    saddle: Saddle
    costume: any
    type: CryopodType

    def _parse(self):
        if self.object is None:
            # ArkSaveLogger.warning_log("Cryopod object is None, cannot parse embedded data")
            return
        
        custom_item_data = self.object.get_array_property_value("CustomItemDatas")

        dino_data = None
        if custom_item_data is not None and len(custom_item_data) > 0:
            dino_data = custom_item_data[0]
            # Check for pelayoris cryopod mod data
            if "Mod_C" in self.object.blueprint:
                dino_data = custom_item_data[2] if len(custom_item_data) > 2 else None
                # no dino if length of custom data is less than 3, empty??
                if dino_data is None:
                    return

        self.embedded_data = EmbeddedCryopodData(dino_data) if dino_data is not None else None

        if self.embedded_data is None:
            self.dino = None
            self.saddle = None
            return
        
        dino_obj, status_obj = self.embedded_data.get_dino_obj()
        
        if dino_obj is not None and status_obj is not None:
            self.dino = TamedDino.from_object(dino_obj, status_obj, self)
            self.dino.save = self.save
            self.dino._location.in_cryopod = True

        # Parse saddle if any.
        saddle_obj = self.embedded_data.get_saddle_obj()
        if saddle_obj is not None:
            self.saddle = Saddle.from_object(saddle_obj)
            if self.saddle is not None:
                # Associate save to the saddle.
                self.saddle.save = self.save

        self.type = None
        if "SCSCryopod" in self.object.blueprint:
            self.type = self.CryopodType.SCS
        elif "Mod_C" in self.object.blueprint:
            self.type = self.CryopodType.PELAYORIS
        elif "ItemDinoball.ItemDinoball_C" in self.object.blueprint:
            self.type = self.CryopodType.DINO_DEPOT
        else:
            self.type = self.CryopodType.NORMAL

        super().__init_props__()


    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)
        self.dino = None
        self.saddle = None
        self.costume = None
        self.embedded_data = None
    
        self._parse()
        

    def is_empty(self):
        return self.dino is None

    def __str__(self):
        if self.is_empty():
            return "Cryopod(empty)"
        
        return "Cryopod(dino={}, lv={}, saddle={}, type={})".format(self.dino.get_short_name(), self.dino.stats.current_level, "no saddle" if self.saddle is None else self.saddle.get_short_name(), self.type.value if self.type is not None else "Unknown")

    def to_json_obj(self):
        base = super().to_json_obj()

        if self.is_empty():
            return base
        
        base["Dino"] = self.dino.to_json_obj() if self.dino is not None else None
        base["Saddle"] = self.saddle.to_json_obj() if self.saddle is not None else None
        base["CryopodType"] = self.type.value if self.type is not None else None
        
        return base

    @staticmethod
    def from_object(obj: ArkGameObject, blueprint: Optional[str] = "/Game/Extinction/CoreBlueprints/Weapons/PrimalItem_WeaponEmptyCryopod.PrimalItem_WeaponEmptyCryopod_C"):
        cryo = Cryopod()
        cryo.object = obj
        cryo.object.blueprint = blueprint
        cryo._parse()

        return cryo


