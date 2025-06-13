from pathlib import Path
from typing import Dict
from uuid import UUID

from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.api.dino_api import DinoApi
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos.tamed_dino import TamedDino
from arkparse.logging import ArkSaveLogger
from arkparse.object_model import ArkGameObject

# save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.ABERRATION).download_save_file(Path.cwd()) # download the save file from an FTP server
save_path = Path.cwd() / "Aberration_WP.ark"
save_path = Path.cwd() / "TheCenter_WP.ark"

looking_for: str = "SuperSpyglass"
save = AsaSave(save_path) 

ArkSaveLogger.enable_debug = True
# save.get_game_object_by_id(UUID("8671e092-d2e9-de41-9ca7-9a55124f16f3"))
# ArkSaveLogger.enable_debug = False
   
save.get_game_objects() # Retrieve all game objects from the save file

uuids = [] # Retrieve all UUIDs of objects with the specified blueprint
for obj in save.parsed_objects.values():
    if looking_for in obj.blueprint:
        print(f"Found {obj.blueprint} with UUID {obj.uuid}")
        uuids.append(obj.uuid)

# Remove the objects which contain specified text in the UUIDs from the save file
for uuid in uuids:
    save.remove_obj_from_db(uuid)
    

# Save the updated save file
save.store_db(Path.cwd() / "updated.ark")

    
