from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
import json
from pathlib import Path
import random

from arkparse.object_model import ArkGameObject
from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase
from arkparse.object_model.misc.object_owner import ObjectOwner
from arkparse.parsing import ArkBinaryParser
from arkparse.parsing.struct.object_reference import ObjectReference
from arkparse.parsing.struct import ActorTransform
from arkparse import AsaSave
from arkparse.utils.json_utils import DefaultJsonEncoder

@dataclass
class Structure(ParsedObjectBase):
    owner: ObjectOwner
    id_: int #StructureID
    max_health: float#MaxHealth
    current_health: float#Health

    location: ActorTransform

    linked_structure_uuids: List[str]#LinkedStructures
    linked_structures = List["Structure"]

    # timestamps
    original_creation_time: float #OriginalCreationTime
    last_enter_stasis_time: float #LastEnterStasisTime
    has_reset_decay_time: bool #bHasResetDecayTime
    saved_when_stasised: bool #bSavedWhenStasised

    # other
    was_placement_snapped: bool #bWasPlacementSnapped
    last_in_ally_range_time_serialized: float #LastInAllyRangeTimeSerialized

    #?
    #StructuresPlacedOnFloor
    #PrimarySnappedStructureChild
    #BedID
    #NextAllowedUseTime
    #PlacedOnFloorStructure
    #LinkedPlayerID
    #LinkedPlayerName
    #bInitializedRotation
    #DoorOpenState
    #CurrentOpenMode
    #CurrentItemCount
    #MyInventoryComponent
    #NetDestructionTime

    def __init__(self, uuid: UUID, save: AsaSave, game_bin: Optional[ArkBinaryParser] = None, game_obj: Optional[ArkGameObject] = None):
        super().__init__(uuid, save=save, game_bin=game_bin, game_obj=game_obj)

        properties = self.object
        self.owner = ObjectOwner(properties)

        self.id_ = properties.get_property_value("StructureID")
        self.max_health = properties.get_property_value("MaxHealth")
        self.current_health = properties.get_property_value("Health", self.max_health)

        self.location = None

        linked: List[ObjectReference] = properties.get_array_property_value("LinkedStructures", [])
        self.linked_structure_uuids = [UUID(link.value) for link in linked]
        self.linked_structures = []

        self.original_creation_time = properties.get_property_value("OriginalCreationTime")
        self.last_enter_stasis_time = properties.get_property_value("LastEnterStasisTime")
        self.has_reset_decay_time = properties.get_property_value("bHasResetDecayTime", False)
        self.saved_when_stasised = properties.get_property_value("bSavedWhenStasised", False)

        self.was_placement_snapped = properties.get_property_value("bWasPlacementSnapped", False)
        self.last_in_ally_range_time_serialized = properties.get_property_value("LastInAllyRangeTimeSerialized")

    def set_actor_transform(self, actor_transform: ActorTransform):
        self.location = actor_transform

    def set_max_health(self, health: float):
        self.max_health = health
        self.binary.replace_float(self.object.find_property("MaxHealth"), float(health))
        self.update_binary()

    def heal(self):
        if self.current_health == self.max_health:
            return
        self.current_health = self.max_health
        self.binary.replace_float(self.object.find_property("Health"), float(self.max_health))
        self.update_binary()

    def set_pincode(self, pin_code: int):
        if not self.object.has_property("CurrentPinCode"):
            raise ValueError("This structure does not have a pincode property.")
        self.binary.replace_u32(self.object.find_property("CurrentPinCode"), pin_code)
        self.update_binary()

    def reidentify(self, new_uuid: UUID = None, update=True):
        new_id = random.randint(0, 2**31 - 1)
        self.id_ = new_id
        self.binary.replace_u32(self.object.find_property("StructureID"), new_id)
        super().reidentify(new_uuid, update=update)

    def remove_from_save(self, save: AsaSave):
        save.remove_obj_from_db(self.object.uuid)

    def is_owned_by(self, owner: ObjectOwner):
        if self.owner.id_ is not None and self.owner.id_ == owner.id_:
            return True
        elif self.owner.player_name is not None and self.owner.player_name == owner.player_name:
            return True
        elif self.owner.tribe_name is not None and self.owner.tribe_name == owner.tribe_name:
            return True
        elif self.owner.tribe_id is not None and self.owner.tribe_id == owner.tribe_id:
            return True
        elif self.owner.original_placer_id is not None and self.owner.original_placer_id == owner.original_placer_id:
            return True
        return False
    
    # def set_owner(self, owner: ObjectOwner, save: AsaSave):
    #     self.owner = owner
    #     save.update_game_object(self.object)

    def store_binary(self, path: Path, loc_only=False, prefix: str = "str_"):
        if not loc_only:
            super().store_binary(path, prefix=prefix)
        self.location.store_json(path, self.object.uuid)

    def __str__(self):
        return f"Structure ({self.get_short_name()}): owned by {self.owner.player_name} {self.current_health}/{self.max_health} {self.location}"
    
    def to_string_complete(self):
        parts = [
            f"Last in ally range time: {self.last_in_ally_range_time_serialized}",
            f"Owner: {self.owner}",
            f"Location: {self.location}",
            f"Max health: {self.max_health}",
            f"Current health: {self.current_health}",
            f"Linked structures: {self.linked_structures}",
            f"Linked structure uuids: {self.linked_structure_uuids}",
            f"Original creation time: {self.original_creation_time}",
            f"Last enter stasis time: {self.last_enter_stasis_time}",
            f"Has reset decay time: {self.has_reset_decay_time}",
            f"Saved when stasised: {self.saved_when_stasised}",
            f"Was placement snapped: {self.was_placement_snapped}",
            f"Last in ally range time serialized: {self.last_in_ally_range_time_serialized}",
        ]
        return "\n".join(parts)

    def get_linked_structures_str(self):
        result = []
        if self.linked_structure_uuids is not None and len(self.linked_structure_uuids) > 0:
            for linked_structure in self.linked_structure_uuids:
                result.append(linked_structure.__str__())
        return result

    def to_json_obj(self):
        # Grab already set properties
        json_obj = { "UUID": self.object.uuid.__str__(),
                     "ItemArchetype": self.object.blueprint,
                     "StructureID": self.id_,
                     "MaxHealth": self.max_health,
                     "Health": self.current_health,
                     "bSavedWhenStasised": self.saved_when_stasised,
                     "bWasPlacementSnapped": self.was_placement_snapped,
                     "bHasResetDecayTime": self.has_reset_decay_time,
                     "LastInAllyRangeTimeSerialized": self.last_in_ally_range_time_serialized,
                     "LastEnterStasisTime": self.last_enter_stasis_time,
                     "OriginalCreationTime": self.original_creation_time }

        # Grab linked structure IDs if there are some
        linked_structures = self.get_linked_structures_str()
        if linked_structures is not None and len(linked_structures) > 0:
            json_obj["LinkedStructureUUIDs"] = linked_structures

        # Grab inventory UUID if it exists
        if self.object.has_property("MyInventoryComponent"):
            inv_comp: ObjectReference = self.object.get_property_value("MyInventoryComponent")
            if inv_comp is not None and inv_comp.value is not None:
                json_obj["InventoryUUID"] = inv_comp.value

        # Grab owner inventory UUID if it exists
        if self.object.has_property("OwnerInventory"):
            owner_inv: ObjectReference = self.object.get_property_value("OwnerInventory")
            if owner_inv is not None and owner_inv.value is not None:
                json_obj["OwnerInventoryUUID"] = owner_inv.value

        # Grab location if it exists
        if self.location is not None:
            json_obj["ActorTransformX"] = self.location.x
            json_obj["ActorTransformY"] = self.location.y
            json_obj["ActorTransformZ"] = self.location.z

        # Grab owner if it exists
        if self.owner is not None:
            json_obj["OwningPlayerID"] = self.owner.id_
            json_obj["OwningPlayerName"] = self.owner.player_name
            json_obj["TargetingTeam"] = self.owner.tribe_id
            json_obj["OwnerName"] = self.owner.tribe_name
            json_obj["OriginalPlacerPlayerID"] = self.owner.original_placer_id

        # Grab remaining properties if any
        if self.object.properties is not None and len(self.object.properties) > 0:
            for prop in self.object.properties:
                if prop is not None:
                    if prop.name is not None and \
                            len(prop.name) > 0 and \
                            "LinkedStructures" not in prop.name and \
                            "StructureID" not in prop.name and \
                            "MaxHealth" not in prop.name and \
                            "Health" not in prop.name and \
                            "bSavedWhenStasised" not in prop.name and \
                            "bWasPlacementSnapped" not in prop.name and \
                            "bHasResetDecayTime" not in prop.name and \
                            "LastInAllyRangeTimeSerialized" not in prop.name and \
                            "LastEnterStasisTime" not in prop.name and \
                            "OriginalCreationTime" not in prop.name and \
                            "MyInventoryComponent" not in prop.name and \
                            "OwnerInventory" not in prop.name:
                        json_obj[prop.name] = self.object.get_property_value(prop.name)

        return json_obj

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
