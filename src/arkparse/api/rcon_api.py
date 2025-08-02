from rcon import source
from pathlib import Path
import json
from typing import List, Dict
from datetime import datetime
from arkparse.logging import ArkSaveLogger
import re
import threading
import uuid

class PlayerDataFiles:
    players_files_path = None

    @staticmethod
    def set_files(players_files_path: Path):
        PlayerDataFiles.players_files_path = players_files_path

class ActivePlayer:
    def __init__(self, string : str):
        split_str = string.split(",")[0].split(".") + [string.split(",")[1]]
        split_str = [x.strip() for x in split_str]
        self.name = split_str[1]
        self.ue_5_id = split_str[2]
        self.real_life_name = ""

        self.id_to_name = {}
        if PlayerDataFiles.players_files_path is not None:
            with open(PlayerDataFiles.players_files_path, 'r') as f:
                id_to_name = json.load(f)
                if self.ue_5_id in id_to_name:
                    self.real_life_name = "" if self.ue_5_id not in id_to_name else "" if "real_name" \
                        not in id_to_name[self.ue_5_id] else id_to_name[self.ue_5_id]["real_name"]

        players_files_path = PlayerDataFiles.players_files_path
        self.players_files_path = players_files_path
        self.playtime = 0 if not self.players_files_path else self.load_playtime()
        
    def __str__(self):
        return f"{self.name} ({self.real_life_name if self.real_life_name != '' else self.ue_5_id})"
    
    def __eq__(self, other: "ActivePlayer"):
        return self.ue_5_id == other.ue_5_id
    
    def get_name(self):
        return self.real_life_name if self.real_life_name != '' else (self.name + "(steam name)")
    
    def load_playtime(self):
        """Load playtime for the player from the playtime file."""
        try:
            with open(self.players_files_path, 'r') as f:
                playtime_data = json.load(f)

                if self.ue_5_id not in playtime_data:
                    return 0
                
                return playtime_data[self.ue_5_id]["playtime"]
        except FileNotFoundError:
            return 0

    def save_playtime(self):
        """Save the player's playtime to the playtime file."""
        try:
            with open(self.players_files_path, 'r') as f:
                player_data = json.load(f)
        except FileNotFoundError:
            player_data = {}

        player_data[self.ue_5_id]["playtime"] = self.playtime
        with open(self.players_files_path, 'w') as f:
            json.dump(player_data, f, indent=4)

    def update_playtime(self, add: int):
        """Update the playtime based on the current session."""
        self.playtime += add
        self.save_playtime()

class GameLogEntry:
    time: datetime
    message_prefix: str
    message: str

    class EntryType:
        CHAT = 0
        GAME = 1
        PLAYER = 2

    def get_player_chat_name(self):
        steam_name = self.message_prefix.split(" ")[0]
        if PlayerDataFiles.players_files_path is not None:
            with open(PlayerDataFiles.players_files_path, 'r') as f:
                players = json.load(f)
                for id in players.keys():
                    p = players[id]
                    if p["steam_name"] == steam_name:
                        if "real_name" in p:
                            return p["real_name"]
        return steam_name
    
    def get_player_ue5_id(self):
        steam_name = self.message_prefix.split(" ")[0]
        if PlayerDataFiles.players_files_path is not None:
            with open(PlayerDataFiles.players_files_path, 'r') as f:
                players = json.load(f)
                for id in players.keys():
                    p = players[id]
                    if p["steam_name"] == steam_name:
                        return id
        return None
    
    def __get_type(self, message: str) -> EntryType:       
        if message.startswith("SERVER:"):
            return self.EntryType.GAME
        
        match = re.match(r"(\d+)\s\(([^)]+)\):", message)
        if match:
            return self.EntryType.PLAYER

        return self.EntryType.CHAT

    def __init__(self, time: str, message: str):
        self.time = datetime.strptime(time, "%Y.%m.%d_%H.%M.%S")
        self.type = self.__get_type(message)
        
        if self.type == self.EntryType.PLAYER or self.type == self.EntryType.GAME:
            self.message_prefix = message.split(":")[0]
            self.message = ':'.join(message.split(":")[1:]).strip()
        else:
            self.message = message
            self.message_prefix = ""

    def __str__(self) -> str:
        return f"{self.__type_str__()}{self.time}: {self.message}"

    def __type_str__(self) -> str:
        if self.type == self.EntryType.PLAYER:
            return ("[" + self.get_player_chat_name() + "]")
        return "[CHAT]" if self.type == self.EntryType.CHAT else "[GAME]"

    def is_newer_than(self, other: "GameLogEntry"):
        return self.time > other.time
    
class RconApi:

    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password

        self.game_log: List[GameLogEntry] = []
        self.last_game_log_entry = None

        # Dictionary to track last seen index for each user
        self.subscribers: Dict[str, int] = {}
        self.lock = threading.Lock()  # To handle concurrent access

    def from_config(config: Path) -> "RconApi":
        with open(config, 'r') as config_file:
            config = json.load(config_file)
        return RconApi(config["host"], config["port"], config["password"])

    def send_cmd(self, cmd: str):
        try:
            with source.Client(self.host, self.port, passwd=self.password, timeout=3) as rcon:
                return rcon.run(cmd)
        except Exception as e:
            ArkSaveLogger.error_log(f"Failed to send command: {e}")
            return None
        
    def send_message(self, message: str):
        return self.send_cmd(f"serverchat [BOT] {message}")
    
        
    def get_active_players(self, p = False):
        players = []
        response = self.send_cmd("listplayers")
        if response is None:
            print("Server not responding")
            return []
        
        for l in response.split("\n"):
            if l.strip() != "":
                if not "No Players Connected" in l:
                    if p:
                        print(l)
                    players.append(ActivePlayer(l))

        return players 
    
    def __update_game_log(self):
        response = self.send_cmd("getgamelog")
        if response is None:
            print("Server not responding")
            return
        if "Server received, But no response!!" in response:
            return
        entries = response.split("\n")
        entries = [e for e in entries if e.strip() != ""]
        # for e in entries:
        #     print(f"Processing log entry: {e}")
        new_entries = [GameLogEntry(time=e.split(" ")[0].strip(':'), message=" ".join(e.split(" ")[1:])) for e in entries]
        self.game_log.extend(new_entries)
        self.last_game_log_entry = new_entries[-1] if len(new_entries) else None
        return new_entries
    
    def subscribe(self):
        """Subscribe a user to the game log."""
        with self.lock:
            handle = str(uuid.uuid4())
            self.subscribers[handle] = len(self.game_log)
            return handle

    def unsubscribe(self, handle: str):
        """Unsubscribe a user from the game log."""
        with self.lock:
            if handle in self.subscribers:
                del self.subscribers[handle]

    def get_new_entries(self, handle: str) -> List[GameLogEntry]:
        """Retrieve new game log entries for a specific user."""
        with self.lock:
            if handle not in self.subscribers:
                raise ValueError(f"Handle '{handle}' is not valid.")

            # Ensure the latest game log is updated
            self.__update_game_log()

            last_seen = self.subscribers[handle]
            new_entries = self.game_log[last_seen:]

            # Update the last seen index for the user
            self.subscribers[handle] = len(self.game_log)

        return new_entries
    
    def import_log(self, path: Path):
        with self.lock:
            try:
                with open(path, 'r') as f:
                    for line_number, line in enumerate(f, start=1):
                        line = line.strip()
                        if not line:
                            continue
                        if ":" not in line:
                            ArkSaveLogger.warning_log(f"Malformed line {line_number}: '{line}'")
                            continue
                        time_str, message = line.split(":", 1)
                        time_str = time_str.strip()
                        message = message.strip()
                        try:
                            time = datetime.strptime(time_str, "%H:%M:%S")
                        except ValueError:
                            raise ValueError(f"Invalid time format on line {line_number}: '{time_str}'")
                        entry = GameLogEntry(time=time, message=message)
                        self.game_log.append(entry)
                # Sort the game_log chronologically after import
                self.game_log.sort(key=lambda entry: entry.time)
                # Update the last_game_log_entry
                if self.game_log:
                    self.last_game_log_entry = self.game_log[-1]
            except FileNotFoundError:
                ArkSaveLogger.warning_log(f"Log file '{path}' not found.")
                raise FileNotFoundError(f"Log file '{path}' not found.")
            except Exception as e:
                ArkSaveLogger.error_log(f"An error occurred while importing the log: {e}")
                raise ValueError(f"An error occurred while importing the log: {e}")
    
    def export_log(self, path: Path):
        with open(path, 'w') as f:
            for entry in self.game_log:
                f.write(str(entry) + "\n")
