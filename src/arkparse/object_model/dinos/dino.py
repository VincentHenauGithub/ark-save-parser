import json
from uuid import UUID
from typing import List
import json

from arkparse.logging.ark_save_logger import ArkSaveLogger
from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase
from arkparse.saves.asa_save import AsaSave
from arkparse.parsing.struct.actor_transform import ActorTransform
from arkparse.parsing.struct.ark_vector import ArkVector
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.enums import ArkDinoTrait
from arkparse.utils.json_utils import DefaultJsonEncoder

from .stats import DinoStats
from ...parsing.struct import ObjectReference


class Dino(ParsedObjectBase):
    id1: int = 0
    id2: int = 0

    is_female: bool = False
    is_cryopodded: bool = False

    gene_traits: List[str] = []
    stats: DinoStats = DinoStats()
    location: ActorTransform = ActorTransform()

    #saddle: Saddle

    def __init_props__(self):
        super().__init_props__()

        self.is_female = self.object.get_property_value("bIsFemale", False)
        self.id1 = self.object.get_property_value("DinoID1")
        self.id2 = self.object.get_property_value("DinoID2")
        self.gene_traits = self.object.get_array_property_value("GeneTraits")
        self.location = ActorTransform(vector=self.object.get_property_value("SavedBaseWorldLocation"))
    
    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)

        if save is not None and self.object.get_property_value("MyCharacterStatusComponent") is not None:
            stat_uuid = self.object.get_property_value("MyCharacterStatusComponent").value
            self.stats = DinoStats(UUID(stat_uuid), save=save)

    def __str__(self) -> str:
        return "Dino(type={}, lv={})".format(self.get_short_name(), self.stats.current_level)

    @staticmethod
    def from_object(dino_obj: ArkGameObject, status_obj: ArkGameObject, dino: "Dino" = None):
        if dino is not None:
            d = dino
        else:
            d: Dino = Dino()
            d.object = dino_obj
            d.__init_props__()

        d.stats = DinoStats.from_object(status_obj)

        return d

    def __get_gene_trait_bytes(self, trait: ArkDinoTrait, level: int, save: AsaSave) -> bytes:
        trait = f"{trait.value}[{level}]"
        trait_id = save.save_context.get_name_id(trait)

        gene_trait_id = save.save_context.get_name_id("GeneTraits")

        if gene_trait_id is None:
            save.add_name_to_name_table("GeneTraits")

        if trait_id is None:
            save.add_name_to_name_table(trait)
            trait_id = save.save_context.get_name_id(trait)
        
        return trait_id.to_bytes(4, byteorder="little") + b'\x00\x00\x00\x00'  
    
    def clear_gene_traits(self, save: AsaSave):
        gt = self.object.get_property_value("GeneTraits")
        self.gene_traits = []

        if gt is None:
            return

        self.binary.set_property_position("GeneTraits")
        self.binary.replace_array("GeneTraits", "NameProperty", None)
        self.object = ArkGameObject(self.object.uuid, self.object.blueprint, self.binary)

        self.update_binary()

    def remove_gene_trait(self, trait: ArkDinoTrait, save: AsaSave):
        self.gene_traits = [t for t in self.gene_traits if not t.startswith(trait.value)]

        gt = self.object.get_property_value("GeneTraits")

        if gt is None:
            return
        
        new_genes = [self.__get_gene_trait_bytes(ArkDinoTrait.from_string(t), int(t.split("[")[1][:-1]), save) for t in self.gene_traits]
        self.binary.set_property_position("GeneTraits")
        self.binary.replace_array("GeneTraits", "NameProperty", new_genes if len(new_genes) > 0 else None)
        self.object = ArkGameObject(self.object.uuid, self.object.blueprint, self.binary)

        self.update_binary()

    def add_gene_trait(self, trait: ArkDinoTrait, level: int, save: AsaSave):
        self.gene_traits.append(f"{trait.value}[{level}]")
        gt = self.object.get_property_value("GeneTraits")

        if gt is None:
            self.binary.set_property_position("SavedBaseWorldLocation")
            self.binary.insert_array("GeneTraits", "NameProperty", [self.__get_gene_trait_bytes(trait, level, save)])
        else:
            new_genes = [self.__get_gene_trait_bytes(ArkDinoTrait.from_string(t), int(t.split("[")[1][:-1]), save) for t in self.gene_traits]
            self.binary.set_property_position("GeneTraits")
            self.binary.replace_array("GeneTraits", "NameProperty", new_genes)
        
        self.object = ArkGameObject(self.object.uuid, self.object.blueprint, self.binary)

        self.update_binary()

    def get_color_set_indices(self) -> List[int]:
        colorSetIndices: List[int] = []
        for i in range(6):
            colorSetIndices.append(self.object.get_property_value("ColorSetIndices", 0, position=i))
        return colorSetIndices

    def get_color_set_names(self) -> List[str]:
        colorSetNames: List[str] = []
        for i in range(6):
            colorSetNames.append(self.object.get_property_value("ColorSetNames", "None", position=i))
        return colorSetNames

    def get_uploaded_from_server_name(self) -> str:
        server_name = self.object.get_property_value("UploadedFromServerName", None)
        if server_name is not None and server_name.startswith("\n"):
            server_name = server_name[1:]
        return server_name

    def to_json_obj(self):
        inv_uuid = None
        inv_comp: ObjectReference = self.object.get_property_value("MyInventoryComponent")
        if inv_comp is not None:
            inv_uuid = UUID(inv_comp.value)
        return { "UUID": self.object.uuid.__str__(),
                 "InventoryUUID": inv_uuid.__str__() if inv_uuid is not None else None,
                 "DinoID1": self.id1,
                 "DinoID2": self.id2,
                 "bIsCryopodded": self.is_cryopodded,
                 "ShortName": self.get_short_name(),
                 "ClassName": "dino",
                 "ItemArchetype": self.object.blueprint,
                 "BaseLevel": self.stats.base_level if self.stats is not None else None,
                 "CurrentLevel": self.stats.current_level if self.stats is not None else None,
                 "BaseStatPoints": self.stats.base_stat_points.to_string_all() if self.stats is not None and self.stats.base_stat_points is not None else None,
                 "AddedStatPoints": self.stats.added_stat_points.to_string_all() if self.stats is not None and self.stats.added_stat_points is not None else None,
                 "MutatedStatPoints": self.stats.mutated_stat_points.to_string_all() if self.stats is not None and self.stats.mutated_stat_points is not None else None,
                 "StatValues": self.stats.stat_values.to_string_all() if self.stats is not None and self.stats.stat_values is not None else None,
                 "GeneTraits": ', '.join(self.gene_traits) if self.gene_traits is not None else None,
                 "ColorSetIndices": self.get_color_set_indices().__str__(),
                 "ColorSetNames": self.get_color_set_names().__str__(),
                 "BabyAge": self.object.get_property_value("BabyAge", None),
                 "ForcedWildBabyAge": self.object.get_property_value("ForcedWildBabyAge", None),
                 "ImprinterName": self.object.get_property_value("ImprinterName", None),
                 "ImprinterPlayerUniqueNetId": self.object.get_property_value("ImprinterPlayerUniqueNetId", None),
                 "OwningPlayerID": self.object.get_property_value("OwningPlayerID", None),
                 "OwningPlayerName": self.object.get_property_value("OwningPlayerName", None),
                 "RandomMutationsFemale": self.object.get_property_value("RandomMutationsFemale", None),
                 "RandomMutationsMale": self.object.get_property_value("RandomMutationsMale", None),
                 "RequiredTameAffinity": self.object.get_property_value("RequiredTameAffinity", None),
                 "StoredXP": self.object.get_property_value("StoredXP", None),
                 "UploadedFromServerName": self.get_uploaded_from_server_name(),
                 "TamedOnServerName": self.object.get_property_value("TamedOnServerName", None),
                 "TamedName": self.object.get_property_value("TamedName", None),
                 "TamerString": self.object.get_property_value("TamerString", None),
                 "TamingTeamID": self.object.get_property_value("TamingTeamID", None),
                 "TargetingTeam": self.object.get_property_value("TargetingTeam", None),
                 "TribeName": self.object.get_property_value("TribeName", None),
                 "bBabyInitiallyUnclaimed": self.object.get_property_value("bBabyInitiallyUnclaimed", None),
                 "bDontWander": self.object.get_property_value("bDontWander", None),
                 "bEnableTamedMating": self.object.get_property_value("bEnableTamedMating", None),
                 "bEnableTamedWandering": self.object.get_property_value("bEnableTamedWandering", None),
                 "bForceDisablingTaming": self.object.get_property_value("bForceDisablingTaming", None),
                 "bIsBaby": self.object.get_property_value("bIsBaby", None),
                 "bIsDead": self.object.get_property_value("bIsDead", None),
                 "bIsFemale": self.object.get_property_value("bIsFemale", None),
                 "bIsFlying": self.object.get_property_value("bIsFlying", None),
                 "bIsParentWildDino": self.object.get_property_value("bIsParentWildDino", None),
                 "bIsSleeping": self.object.get_property_value("bIsSleeping", None),
                 "bSavedWhenStasised": self.object.get_property_value("bSavedWhenStasised", None),
                 "DinoDownloadedAtTime": self.object.get_property_value("DinoDownloadedAtTime", None),
                 "LastEnterStasisTime": self.object.get_property_value("LastEnterStasisTime", None),
                 "LastInAllyRangeSerialized": self.object.get_property_value("LastInAllyRangeSerialized", None),
                 "LastUnstasisStructureTime": self.object.get_property_value("LastUnstasisStructureTime", None),
                 "LastUpdatedBabyAgeAtTime": self.object.get_property_value("LastUpdatedBabyAgeAtTime", None),
                 "LastUpdatedGestationAtTime": self.object.get_property_value("LastUpdatedGestationAtTime", None),
                 "LastUpdatedMatingAtTime": self.object.get_property_value("LastUpdatedMatingAtTime", None),
                 "NextAllowedMatingTime": self.object.get_property_value("NextAllowedMatingTime", None),
                 "OriginalCreationTime": self.object.get_property_value("OriginalCreationTime", None),
                 "TamedAtTime": self.object.get_property_value("TamedAtTime", None),
                 "TamedTimeStamp": self.object.get_property_value("TamedTimeStamp", None),
                 "ActorTransformX": self.location.x if self.location is not None else None,
                 "ActorTransformY": self.location.y if self.location is not None else None,
                 "ActorTransformZ": self.location.z if self.location is not None else None }

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)

    def store_binary(self, path, name = None, prefix = "obj_", no_suffix=False):
        loc_name = name if name is not None else str(self.object.uuid)
        self.stats.store_binary(path, name, prefix="status_", no_suffix=no_suffix)
        self.location.store_json(path, loc_name)
        return super().store_binary(path, name, prefix=prefix, no_suffix=no_suffix)

    def set_location(self, location: ActorTransform, save: AsaSave):
        current_location = self.object.find_property("SavedBaseWorldLocation")
        
        if current_location is None:
            raise ValueError("SavedBaseWorldLocation property not found in the object")

        as_vector: ArkVector = ArkVector(x=location.x, y=location.y, z=location.z)
        self.binary.replace_struct_property(current_location, as_vector.to_bytes())
        self.object = ArkGameObject(self.object.uuid, self.object.blueprint, self.binary)

        save.modify_actor_transform(self.object.uuid, location.to_bytes())
        self.update_binary()
        self.location = location
