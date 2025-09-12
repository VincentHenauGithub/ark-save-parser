from dataclasses import dataclass
from arkparse.parsing import ArkPropertyContainer
from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.logging import ArkSaveLogger

from arkparse.player.ark_player import ArkPlayer
from arkparse.ark_tribe import ArkTribe
from arkparse.object_model.ark_game_object import ArkGameObject

@dataclass
class ObjectOwner:
    original_placer_id: int = None      #OriginalPlacerPlayerID
    tribe_name: str = None              #OwnerName (tribename)
    player_name: str = None             #OwningPlayerName
    id_: int = None                     #OwningPlayerID
    tribe_id: int = None                #TargetingTeam

    def __init__(self, properties: ArkPropertyContainer = None):
        if properties is None:
            return
        self.properties = properties
        self.original_placer_id = properties.get_property_value("OriginalPlacerPlayerID")
        self.tribe_name = properties.get_property_value("OwnerName")
        self.player_name = properties.get_property_value("OwningPlayerName")
        self.id_ = properties.get_property_value("OwningPlayerID")
        self.tribe_id = properties.get_property_value("TargetingTeam")

    def __eq__(self, other: "ObjectOwner"):
        if not isinstance(other, ObjectOwner):
            return False
        if self.tribe_id is not None and other.tribe_id is not None:
            if self.tribe_id != other.tribe_id:
                return False
        if self.id_ is not None and other.id_ is not None:
            if self.id_ != other.id_:
                return False
        return True

    def set_in_binary(self, binary: ArkBinaryParser):
        ArkSaveLogger.set_file(binary, "debug.bin")
        
        if binary is not None:
            if self.original_placer_id is not None:
                binary.replace_u32(self.properties.find_property("OriginalPlacerPlayerID"), self.original_placer_id)
            if self.tribe_name is not None:
                binary.replace_string(self.properties.find_property("OwnerName"), self.tribe_name)
                self.properties = ArkGameObject(uuid='', blueprint='', binary_reader=binary) # align after potential move of positions
            if self.player_name is not None:
                binary.replace_string(self.properties.find_property("OwningPlayerName"), self.player_name)
                self.properties = ArkGameObject(uuid='', blueprint='', binary_reader=binary) # align after potential move of positions
            if self.id_ is not None:
                binary.replace_u32(self.properties.find_property("OwningPlayerID"), self.id_)
            if self.tribe_id is not None:
                binary.replace_u32(self.properties.find_property("TargetingTeam"), self.tribe_id)

        return binary

    def __str__(self) -> str:
        return f"\"{self.player_name}\" ({self.id_}) of tribe \"{self.tribe_name}\" ({self.tribe_id})"# (originally placed by {self.original_placer_id})"
    
    def set_tribe(self, tribe_id: int, tribe_name: str="None"):
        self.tribe_id = tribe_id
        self.tribe_name = tribe_name

    def set_player(self, player_id: int=0, player_name: str="None"):
        self.id_ = player_id
        self.player_name = player_name
        self.original_placer_id = player_id
    
    def replace_self_with(self, other: "ObjectOwner", binary: ArkBinaryParser = None):
        self.original_placer_id = None if self.original_placer_id is None else other.original_placer_id
        self.tribe_name = None if self.tribe_name is  None else other.tribe_name
        self.tribe_id = None if self.tribe_id is  None else other.tribe_id
        self.player_name = None if self.player_name is  None else other.player_name
        self.id_ = None if self.id_ is  None else other.id_

        if binary is not None:
            self.set_in_binary(binary)

    def serialize(self):
        return {
            "original_placer_id": self.original_placer_id,
            "tribe_name": self.tribe_name,
            "player_name": self.player_name,
            "id_": self.id_,
            "tribe_id": self.tribe_id
        }
    
    @staticmethod
    def from_profile(profile: ArkPlayer, tribe: ArkTribe):
        obj = ObjectOwner()
        obj.id_ = profile.id_
        obj.tribe_name = tribe.name
        obj.player_name = profile.name
        obj.original_placer_id = profile.id_
        obj.tribe_id = tribe.tribe_id

        return obj