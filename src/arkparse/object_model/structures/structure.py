from dataclasses import dataclass
from typing import List
from uuid import UUID
import json
from pathlib import Path
import random

from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase
from arkparse.object_model.misc.object_owner import ObjectOwner
from arkparse.parsing.struct.object_reference import ObjectReference
from arkparse.parsing.struct import ActorTransform
from arkparse.parsing import ArkBinaryParser
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

    def __init__(self, uuid: UUID, save: AsaSave):
        super().__init__(uuid, save=save)

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

    def heal(self):
        if self.current_health == self.max_health:
            return
        self.current_health = self.max_health
        self.binary.replace_float(self.object.find_property("Health"), float(self.max_health))

    def reidentify(self, new_uuid: UUID = None, update=True):
        new_id = random.randint(0, 2**32 - 1)
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
        result = ""
        if self.linked_structures is not None:
            for linked_structure in self.linked_structure_uuids:
                if len(result) > 0:
                    result = result + ","
                result = result + linked_structure.__str__()
        return result

    def to_json_obj(self):
        # Grab already set properties
        retj = { "UUID": self.object.uuid.__str__(),
                 "LinkedStructureUUIDS": self.get_linked_structures_str(),
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

        # Grab inventory UUID if it exists
        inv_uuid = None
        if self.object.has_property("MyInventoryComponent"):
            inv_comp: ObjectReference = self.object.get_property_value("MyInventoryComponent", default=None)
            if inv_comp is not None:
                inv_uuid = UUID(inv_comp.value)
        if inv_uuid is not None:
            retj["InventoryUUID"] = inv_uuid.__str__()

        # Grab owner inventory UUID if it exists
        owner_inv_uuid = None
        if self.object.has_property("OwnerInventory"):
            owner_in: ObjectReference = self.object.get_property_value("OwnerInventory", default=None)
            if owner_in is not None:
                owner_inv_uuid = UUID(owner_in.value)
        if owner_inv_uuid is not None:
            retj["OwnerInventoryUUID"] = owner_inv_uuid.__str__()

        # Grab location if it exists
        if self.location is not None:
            retj["ActorTransformX"] = self.location.x
            retj["ActorTransformY"] = self.location.y
            retj["ActorTransformZ"] = self.location.z

        # Grab owner if it exists
        if self.owner is not None:
            retj["OwningPlayerID"] = self.owner.id_
            retj["OwningPlayerName"] = self.owner.player_name
            retj["TargetingTeam"] = self.owner.tribe_id
            retj["OwnerName"] = self.owner.tribe_name
            retj["OriginalPlacerPlayerID"] = self.owner.original_placer_id

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
                        prop_value = self.object.get_property_value(prop.name, None)
                        retj[prop.name] = prop_value
                        #print("Prop: " + prop.name, flush=True)
                        #teststr = json.dumps(prop_value)

        return retj

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
