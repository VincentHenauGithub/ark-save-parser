import uuid
from typing import List, Dict, Optional
from pathlib import Path
from uuid import UUID

from arkparse.player.ark_player import ArkPlayer
from arkparse.ark_tribe import ArkTribe
from arkparse.saves.asa_save import AsaSave
from arkparse.parsing import ArkBinaryParser
from arkparse.classes.player import Player
from arkparse.parsing.game_object_reader_configuration import GameObjectReaderConfiguration
from arkparse.saves.save_connection import SaveConnection
from arkparse.utils import TEMP_FILES_DIR
from arkparse.logging import ArkSaveLogger

from arkparse.object_model.misc.dino_owner import DinoOwner
from arkparse.object_model.misc.object_owner import ObjectOwner
from arkparse.object_model.ark_game_object import ArkGameObject

class _TribeAndPlayerData:
    HEADER_OFFSET_ADJUSTMENT = 4
    TRIBE_HEADER_BASE_OFFSET = 4

    # "/Script/ShooterGame.PrimalTribeData"
    TRIBE_DATA_NAME = bytes([
        0x2f, 0x53, 0x63, 0x72, 0x69, 0x70, 0x74, 0x2f, 0x53, 0x68, 0x6f, 0x6f, 0x74, 0x65, 0x72, 0x47,
        0x61, 0x6d, 0x65, 0x2e, 0x50, 0x72, 0x69, 0x6d, 0x61, 0x6c, 0x54, 0x72, 0x69, 0x62, 0x65,
        0x44, 0x61, 0x74, 0x61, 0x00
    ])  
    
    # "Game/PrimalEarth/CoreBlueprints/PrimalPlayerDataBP.PrimalPlayerDataBP_C"
    PLAYER_DATA_NAME = bytes([
        0x47, 0x61, 0x6d, 0x65, 0x2f, 0x50, 0x72, 0x69, 0x6d, 0x61, 0x6c, 0x45, 0x61, 0x72, 0x74, 0x68,
        0x2f, 0x43, 0x6f, 0x72, 0x65, 0x42, 0x6c, 0x75, 0x65, 0x70, 0x72, 0x69, 0x6e, 0x74, 0x73, 0x2f,
        0x50, 0x72, 0x69, 0x6d, 0x61, 0x6c, 0x50, 0x6c, 0x61, 0x79, 0x65, 0x72, 0x44, 0x61, 0x74, 0x61,
        0x42, 0x50, 0x2e, 0x50, 0x72, 0x69, 0x6d, 0x61, 0x6c, 0x50, 0x6c, 0x61, 0x79, 0x65, 0x72, 0x44,
        0x61, 0x74, 0x61, 0x42, 0x50, 0x5f, 0x43, 0x00
    ])

    def __init__(self, store_data: ArkBinaryParser = None):
        self.data = store_data
        
        self.tribe_data_pointers: Dict[uuid.UUID, list] = {}
        self.player_data_pointers: Dict[uuid.UUID, list] = {}
        self.tribes_data: Dict[uuid.UUID, bytes] = {}
        self.players_data: Dict[uuid.UUID, bytes] = {}
        if self.data is not None:
            ArkSaveLogger.set_file(self.data, "TribeAndPlayerData.bin")
            self.initialize_data()
            ArkSaveLogger.api_log(f"Found {len(self.tribe_data_pointers)} tribe data pointers and {len(self.player_data_pointers)} player data pointers in the save data.")

    def initialize_data(self) -> None:
        # Read initial flag (unused)
        _ = self.data.read_boolean()
        self._get_tribe_offsets()
        self._get_player_offsets()

    def _get_tribe_offsets(self) -> None:
        positions = self.data.find_byte_sequence(self.TRIBE_DATA_NAME)
        # print(f"Found {len(positions)} tribe data offsets in the save data.")
        for pos in positions:
            # Get ID
            # print(f"Tribe data found at offset: {pos}")
            self.data.set_position(pos - 20)
            uuid_bytes = self.data.read_bytes(16)
            uuid_pos = self.data.find_byte_sequence(uuid_bytes)
            tribe_uuid = SaveConnection.byte_array_to_uuid(uuid_bytes)

            ArkSaveLogger.api_log(f"Found tribe UUID at position: {uuid_pos[0]}, second UUID position: {uuid_pos[1]}")
            offset = pos - 36
            size = uuid_pos[1] - offset
            self.tribe_data_pointers[tribe_uuid] = [uuid_bytes, offset+1, size]

    def _get_player_offsets(self) -> None:
        pattern = bytes([0x4E, 0x6F, 0x6E, 0x65])
        positions = self.data.find_byte_sequence(self.PLAYER_DATA_NAME)
        # print(f"Found {len(positions)} player data offsets in the save data.")
        for i, pos in enumerate(positions):
            # Get ID
            self.data.set_position(pos - 20)
            uuid_bytes = self.data.read_bytes(16)
            player_uuid = SaveConnection.byte_array_to_uuid(uuid_bytes)
            offset = pos - 36

            next_player_data = positions[i + 1] if i + 1 < len(positions) else None
            if not next_player_data is None:
                last_none = self.data.find_last_byte_sequence_before(pattern, next_player_data)
                if not last_none is None:
                    end_pos = last_none + 4
                    size = end_pos - offset
                    ArkSaveLogger.api_log(f"Player UUID: {uuid_bytes.hex()}, Offset: {offset}, Size: {size}, End: {offset+size}, Next Player Data: {next_player_data}")
                    self.player_data_pointers[player_uuid] = [uuid_bytes, offset, size+1]

    def get_ark_tribe_raw_data(self, index: uuid.UUID) -> Optional[bytes]:
        pointer = self.tribe_data_pointers[index]
        if not pointer:
            return None
        self.data.set_position(pointer[1])
        return self.data.read_bytes(pointer[2])

    def get_ark_profile_raw_data(self, index: uuid.UUID) -> Optional[bytes]:
        pointer = self.player_data_pointers[index]
        if not pointer:
            return None
        self.data.set_position(pointer[1])
        return self.data.read_bytes(pointer[2]) + bytes([0x00, 0x01, 0x00, 0x00, 0x00])  + pointer[0]
    
class PlayerApi:
    class StatType:
        LOWEST = 0
        HIGHEST = 1
        AVERAGE = 2
        TOTAL = 3

    class Stat:
        DEATHS = 0
        LEVEL = 1
        XP = 2

    class OwnerType:
        OBJECT = 0
        DINO = 1

    def __init__(self, save: AsaSave, ignore_error: bool = False, no_pawns: bool = False, bypass_inventory: bool = False, pawn_objects: Optional[list[ArkGameObject]] = None):
        self.players: List[ArkPlayer] = []
        self.tribes: List[ArkTribe] = []
        self.tribe_to_player_map: Dict[int, List[ArkPlayer]] = {}
        self.save: AsaSave = save
        self.pawns: Optional[Dict[UUID, ArkGameObject]] = None

        self.profile_paths: List[Path] = []
        self.tribe_paths: List[Path] = []
        self.ignore_error = ignore_error

        self.from_store = True
        if save.profile_data_in_saves() == False:
            ArkSaveLogger.api_log("Profile data not found in save, checking database")
            self.from_store = False

        if self.save is not None and not no_pawns:
            ArkSaveLogger.api_log(f"Retrieving player pawns")
            self.__init_pawns()
        elif pawn_objects is not None:
            self.pawns = {}
            for pawn in pawn_objects:
                if not pawn is None:
                    self.pawns[pawn.uuid] = pawn

        if self.from_store:
            self.__get_files_from_db()
        elif save.save_dir is not None:
            self.get_files_from_directory(save.save_dir)

        if len(self.profile_paths) == 0 and len(self.tribe_paths) == 0 and not self.from_store:
            ArkSaveLogger.api_log("No profile or tribe data found")
        else:
            ArkSaveLogger.api_log(f"Found {len(self.profile_paths)} profile files and {len(self.tribe_paths)} tribe files in the save directory")

        ArkSaveLogger.api_log("Parsing player and tribe data from files")
        self.__update_files(bypass_inventory)

    def __del__(self):
        ArkSaveLogger.api_log("Stopping PlayerApi")
        self.players = {}
        self.tribes = {}
        self.tribe_to_player_map = {}
        self.pawns = {}
        self.save = None
        ArkSaveLogger.api_log("PlayerApi stopped")

    def __init_pawns(self):
        if self.save is not None:
            pawn_bps = [Player.pawn_female, Player.pawn_male]
            config = GameObjectReaderConfiguration(
                blueprint_name_filter=lambda name: name is not None and name in pawn_bps,
            )
            self.pawns = self.save.get_game_objects(config)

    def __store_as_file(self, data: bytes, file_name: str):
        output_dir = TEMP_FILES_DIR
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / file_name
        with open(path, "wb") as f:
            f.write(data)
        return path
    
    def __get_files_from_db(self):
        if self.save is None:
            raise ValueError("Save not provided")
        
        if self.save.get_custom_value("GameModeCustomBytes") is None:
            raise ValueError("No GameModeCustomBytes found in the save data")
        
        self.data = _TribeAndPlayerData(self.save.get_custom_value("GameModeCustomBytes"))

        for key, value in self.data.player_data_pointers.items():
            self.data.players_data[key] = self.data.get_ark_profile_raw_data(key)

        for key, value in self.data.tribe_data_pointers.items():
            self.data.tribes_data[key] = self.data.get_ark_tribe_raw_data(key)

    def get_files_from_directory(self, directory: Path):
        for path in directory.glob("*.arkprofile"):
            self.profile_paths.append(path)
        for path in directory.glob("*.arktribe"):
            self.tribe_paths.append(path)

    def __update_files(self, bypass_inventory: bool):
        new_players: Dict[int, ArkPlayer] = {}
        new_tribes: Dict[int, ArkTribe] = {}
        new_tribe_to_player: Dict[int, List[ArkPlayer]] = {}

        if not self.from_store:
            index: int = 0
            self.data = _TribeAndPlayerData()
            for path in self.profile_paths:
                self.data.players_data[uuid.UUID(int=index)] = path.read_bytes()
                index += 1
            index = 0
            for path in self.tribe_paths:
                self.data.tribes_data[uuid.UUID(int=index)] = path.read_bytes()
                index += 1

        for player_uuid, player_data in self.data.players_data.items():
            try:
                parsed_player: ArkPlayer = ArkPlayer(player_data, self.from_store)
            except Exception as e:
                if "Unsupported archive version" in str(e):
                    ArkSaveLogger.api_log(f"Skipping player data {player_uuid} due to unsupported archive version: {e}")
                    continue
                if self.ignore_error:
                    continue
                raise e
            new_players[parsed_player.id_] = parsed_player

        if not self.pawns is None:
            for player in new_players.values():
                for pawn in self.pawns.values():
                    if player.id_ == pawn.get_property_value("LinkedPlayerDataID"):
                        player.get_location_and_inventory(self.save, pawn, bypass_inventory)
                        break

        for tribe_uuid, tribe_data in self.data.tribes_data.items():
            try:
                parsed_tribe: ArkTribe = ArkTribe(tribe_data, self.from_store)
            except Exception as e:
                if "Unsupported archive version" in str(e):
                    ArkSaveLogger.api_log(f"Skipping player data {tribe_uuid} due to unsupported archive version: {e}")
                    continue
                if self.ignore_error:
                    continue
                raise e

            players = []
            for member_id in parsed_tribe.member_ids:
                if new_players.__contains__(member_id):
                    players.append(new_players[member_id])
                else:
                    ArkSaveLogger.api_log(f"Player with ID {member_id} not found in player list")

            new_tribes[parsed_tribe.tribe_id] = parsed_tribe
            new_tribe_to_player[parsed_tribe.tribe_id] = players

        self.players = list(new_players.values())
        self.tribes = list(new_tribes.values())
        self.tribe_to_player_map = new_tribe_to_player

    def __calc_stat(self, stat: List[int], stat_type: int):
        if stat_type == self.StatType.LOWEST:
            return min(stat)
        elif stat_type == self.StatType.HIGHEST:
            return max(stat)
        elif stat_type == self.StatType.AVERAGE:
            return sum(stat) / len(stat)
        elif stat_type == self.StatType.TOTAL:
            return sum(stat)
        
    def __get_stat(self, stat: int):
        if stat == self.Stat.DEATHS:
            return self.get_deaths(as_dict=True)
        elif stat == self.Stat.LEVEL:
            return self.get_level(as_dict=True)
        elif stat == self.Stat.XP:
            return self.get_xp(as_dict=True)
        
    def get_deaths(self, player: str = None, stat_type: int = StatType.TOTAL, as_dict: bool = False):
        deaths = []
        dict = {}

        for p in self.players:
            # print(f"Player {p.name} with ID {p.id_} has {p.nr_of_deaths} deaths")
            if p.name == player or player is None:
                deaths.append(p.nr_of_deaths)
                dict[p.id_] = p.nr_of_deaths

        return self.__calc_stat(deaths, stat_type) if not as_dict else dict
    
    def get_level(self, player: str = None, stat_type: int = StatType.TOTAL, as_dict: bool = False):
        levels = []
        dict = {}

        for p in self.players:
            if p.name == player or player is None:
                levels.append(p.stats.level)
                dict[p.id_] = p.stats.level

        return self.__calc_stat(levels, stat_type) if not as_dict else dict

    def get_xp(self, player: str = None, stat_type: int = StatType.TOTAL, as_dict: bool = False):
        xp = []
        dict = {}

        for p in self.players:
            if p.name == player:
                xp.append(p.stats.experience)
                dict[p.id_] = p.stats.experience

        return self.__calc_stat(xp, stat_type) if not as_dict else dict

    def get_tribe(self, tribe_id: int):
        for t in self.tribes:
            if t.tribe_id == tribe_id:
                return t
        return None
    
    def get_player_with(self, stat: int, stat_type: int = StatType.HIGHEST):
        istat = self.__get_stat(stat)
        player: Optional[ArkPlayer] = None
        value: int = 0
        player_id: int = -1
        
        if stat_type == self.StatType.LOWEST:
            player_id = min(istat, key=istat.get)
            value = istat[player_id]
        elif stat_type == self.StatType.HIGHEST:
            player_id = max(istat, key=istat.get)
            value = istat[player_id]
        elif stat_type == self.StatType.AVERAGE:
            player_id = max(istat, key=istat.get)
            value = istat[player_id]
        elif stat_type == self.StatType.TOTAL:
            player_id = max(istat, key=istat.get)
            value = istat[player_id]

        if not player_id == -1:
            for p in self.players:
                if p.id_ == player_id:
                    player = p
                    break
        
        return player, value
    
    def get_container_of_inventory_by_uuid(self, inv_uuid: UUID, save: AsaSave = None):
        for player in self.players:
            inventory = self.get_player_inventory(player, save)
            if inventory is not None and inventory.object.uuid == inv_uuid:
                return player
        return None
    
    def get_player_by_platform_name(self, name: str):
        for p in self.players:
            if p.name == name:
                return p
        return None
    
    def get_tribe_of(self, player: ArkPlayer):
        for t in self.tribes:
            if player.tribe == t.tribe_id:
                return t
        return None
    
    def get_as_owner(self, owner_type: int, player_id: int= None, ue5_id: str = None, tribe_id: int = None, tribe_name: str = None):
        player = None
        tribe = None

        for p in self.players:
            if player_id is not None and p.id_ == player_id:
                player = p
                break
            elif ue5_id is not None and p.unique_id == ue5_id:
                player = p
                break
        
        if player is None and tribe_id is None and tribe_name is None:
            raise ValueError("Player not found")
        
        if player:
            tribe = self.get_tribe_of(player)
        else:
            for t in self.tribes:
                if tribe_id is not None and t.tribe_id == tribe_id:
                    tribe = t
                    break
                elif tribe_name is not None and t.name == tribe_name:
                    tribe = t
                    break
        
        if tribe is None:
            raise ValueError("Tribe not found")

        if owner_type == self.OwnerType.OBJECT:
            return ObjectOwner.from_profile(player, tribe)
        elif owner_type == self.OwnerType.DINO:
            return DinoOwner.from_profile(tribe, player)
        return None
    
    def __check_pawns(self, save: AsaSave):
        if save is None and self.save is None:
            raise ValueError("Save not provided")
        
        if save is not None:
            self.save = save
        
        if self.pawns is None:
            self.__init_pawns()
    
    def get_player_pawn(self, player: ArkPlayer, save: AsaSave = None):
        self.__check_pawns(save)
        for _, pawn in self.pawns.items():
            player_id = pawn.get_property_value("LinkedPlayerDataID")
            if player_id == player.id_:
                return pawn
        return None
    
    def get_player_inventory(self, player: ArkPlayer, save: AsaSave = None):
        if player.inventory:
            return player.inventory
        
        self.__check_pawns(save)
        pawn = self.get_player_pawn(player, self.save)
        player.get_location_and_inventory(save, pawn)

        return player.inventory
    
    def get_player_location(self, player: ArkPlayer, save: AsaSave = None):
        if player.location:
            return player.location
        
        self.__check_pawns(save)
        pawn = self.get_player_pawn(player, self.save)
        if pawn is not None:
            player.get_location_and_inventory(save, pawn)

        return player.location
    
    def generate_player_id(self, min=13781378, max=997533501) -> int:
        import random
        player_id = random.randint(min, max)
        while any(p.id_ == player_id for p in self.players):
            player_id = random.randint(min, max)
        return player_id
    
    def generate_tribe_id(self, min=1022488265, max=1914242586) -> int:
        import random
        tribe_id = random.randint(min, max)
        while any(t.tribe_id == tribe_id for t in self.tribes):
            tribe_id = random.randint(min, max)
        return tribe_id

    # def add_to_player_inventory(self, player: ArkPlayer, item: ArkGameObject, save: AsaSave = None):
    #     if player is None:
    #         raise ValueError("Player not found")
        
    #     self.__check_pawns(self.save)
    #     inventory: Inventory = self.get_player_inventory(player, self.save)
    #     self.save.add_obj_to_db(item.uuid)
    #     inventory.add_item(item, self.save)

