import json
from uuid import UUID
from typing import List, Optional
import random

from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase
from arkparse.saves.asa_save import AsaSave
from arkparse.parsing.struct.actor_transform import ActorTransform
from arkparse.parsing.struct.ark_vector import ArkVector
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.enums import ArkDinoTrait
from arkparse.utils.json_utils import DefaultJsonEncoder
from .dino_ai_controller import DinoAiController

from .stats import DinoStats
from ...parsing import ArkBinaryParser
from ...parsing.struct import ObjectReference


class Dino(ParsedObjectBase):
    id1: int = 0
    id2: int = 0

    is_female: bool = False
    is_cryopodded: bool = False
    is_dead: bool = False

    ai_controller: DinoAiController = None

    gene_traits: List[str] = []
    stats: DinoStats = DinoStats()
    _location: ActorTransform = ActorTransform()

    #saddle: Saddle

    def __init_props__(self):
        super().__init_props__()

        self.is_female = self.object.get_property_value("bIsFemale", False)
        self.id1 = self.object.get_property_value("DinoID1")
        self.id2 = self.object.get_property_value("DinoID2")
        self.gene_traits = self.object.get_array_property_value("GeneTraits")
        self.is_dead = self.object.get_property_value("bIsDead", False)
        self._location = ActorTransform(vector=self.object.get_property_value("SavedBaseWorldLocation"))
    
    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)

        if save is not None and self.object.get_property_value("MyCharacterStatusComponent") is not None:
            stat_uuid = self.object.get_property_value("MyCharacterStatusComponent").value
            self.stats = DinoStats(UUID(stat_uuid), save=save)

        if save is not None and self.object.get_property_value("Owner") is not None:
            if self.save.is_in_db(UUID(self.object.get_property_value("Owner").value)):
                ai_uuid = self.object.get_property_value("Owner").value
                self.ai_controller = DinoAiController(UUID(ai_uuid), save=save)

    def __str__(self) -> str:
        return "Dino(type={}, lv={})".format(self.get_short_name(), self.stats.current_level)
    
    @property
    def location(self) -> ActorTransform:
        return self._location

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
        # Grab already set properties
        json_obj = { "UUID": self.object.uuid.__str__(),
                     "DinoID1": self.id1,
                     "DinoID2": self.id2,
                     "bIsCryopodded": self.is_cryopodded,
                     "bIsFemale": self.is_female,
                     "ShortName": self.get_short_name(),
                     "ClassName": "dino",
                     "ItemArchetype": self.object.blueprint }

        # Grab dino location if it exists
        if self._location is not None:
            json_obj["ActorTransformX"] = self._location.x
            json_obj["ActorTransformY"] = self._location.y
            json_obj["ActorTransformZ"] = self._location.z

        # Grab dino inventory UUID if it exists
        if self.object.has_property("MyInventoryComponent"):
            inv_comp = self.object.get_property_value("MyInventoryComponent")
            if inv_comp is not None and inv_comp.value is not None:
                json_obj["InventoryUUID"] = inv_comp.value

        # Grab owner inventory UUID if it exists
        if self.object.has_property("OwnerInventory"):
            owner_inv: ObjectReference = self.object.get_property_value("OwnerInventory")
            if owner_inv is not None and owner_inv.value is not None:
                json_obj["OwnerInventoryUUID"] = owner_inv.value

        # Grab stats if they exists
        if self.stats is not None:
            json_obj["BaseLevel"] = self.stats.base_level
            json_obj["CurrentLevel"] = self.stats.current_level
            if self.stats.base_stat_points is not None:
                json_obj["BaseStatPoints"] = self.stats.base_stat_points.to_string_all()
            if self.stats.added_stat_points is not None:
                json_obj["AddedStatPoints"] = self.stats.added_stat_points.to_string_all()
            if self.stats.mutated_stat_points is not None:
                json_obj["MutatedStatPoints"] = self.stats.mutated_stat_points.to_string_all()
            if self.stats.stat_values is not None:
                json_obj["StatValues"] = self.stats.stat_values.to_string_all()

        # Grab gene traits if they exists
        if self.gene_traits is not None:
            json_obj["GeneTraits"] = self.gene_traits

        # Grab colors if they exists
        color_set_indices = self.get_color_set_indices()
        if color_set_indices is not None:
            json_obj["ColorSetIndices"] = color_set_indices.__str__()
        color_set_names = self.get_color_set_names()
        if color_set_names is not None:
            json_obj["ColorSetNames"] = color_set_names.__str__()

        # Grab remaining properties if any
        if self.object.properties is not None and len(self.object.properties) > 0:
            for prop in self.object.properties:
                if prop is not None and \
                        prop.name is not None and \
                        len(prop.name) > 0 and \
                        "DinoID1" not in prop.name and \
                        "DinoID2" not in prop.name and \
                        "bIsFemale" not in prop.name and \
                        "SavedBaseWorldLocation" not in prop.name and \
                        "MyInventoryComponent" not in prop.name and \
                        "OwnerInventory" not in prop.name and \
                        "GeneTraits" not in prop.name and \
                        "ColorSetIndices" not in prop.name and \
                        "ColorSetNames" not in prop.name:
                    json_obj[prop.name] = self.object.get_property_value(prop.name)

        return json_obj

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)

    def store_binary(self, path, name = None, prefix = "obj_", no_suffix=False):
        loc_name = name if name is not None else str(self.object.uuid)
        self.stats.store_binary(path, name, prefix="status_", no_suffix=no_suffix)
        if self.ai_controller is not None:
            self.ai_controller.store_binary(path, name, prefix="ai_", no_suffix=no_suffix)
        self.location.store_json(path, loc_name)
        return super().store_binary(path, name, prefix=prefix, no_suffix=no_suffix)

    def set_location(self, location: ActorTransform):
        current_location = self.object.find_property("SavedBaseWorldLocation")
        
        if current_location is None:
            raise ValueError("SavedBaseWorldLocation property not found in the object")

        as_vector: ArkVector = ArkVector(x=location.x, y=location.y, z=location.z)
        self.binary.replace_struct_property(current_location, as_vector.to_bytes())
        self.object = ArkGameObject(self.object.uuid, self.object.blueprint, self.binary)

        self.save.modify_actor_transform(self.object.uuid, location.to_bytes())
        self.update_binary()
        self._location = location

    def heal(self):
        self.stats.heal()

    def disable_wandering(self):
        """
        Disables the wandering behavior of the dino.
        """
        if self.object.has_property("bEnableTamedWandering"):
            self.binary.replace_boolean(self.object.find_property("bEnableTamedWandering"), False)
            self.update_binary()

    def reidentify(self, new_uuid: UUID = None, update=True):
        new_id_1 = random.randint(0, 2**31 - 1)
        new_id_2 = random.randint(0, 2**31 - 1)
        self.id1 = new_id_1
        self.id2 = new_id_2
        self.binary.replace_u32(self.object.find_property("DinoID1"), new_id_1)
        self.binary.replace_u32(self.object.find_property("DinoID2"), new_id_2)

        current_time_stamp = self.save.save_context.game_time

        for prop in [
            "TamingLastFoodConsumptionTime",
            "TamedAtTime",
            "LastTameConsumedFoodTime",
            "LastInAllyRangeSerialized",
            "LastTimeUpdatedCharacterStatusComponent",
            "LastEnterStasisTime",
            "OriginalCreationTime",
            "LastUpdatedBabyAgeAtTime",
            "LastEggSpawnChanceTime",
            
            
        ]:
            p = self.object.find_property(prop)
            if p is not None:
                self.binary.replace_double(p, current_time_stamp)

        super().reidentify(new_uuid, update=update)

