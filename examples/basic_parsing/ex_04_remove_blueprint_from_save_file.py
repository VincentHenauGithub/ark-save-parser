from pathlib import Path
from typing import Dict
from uuid import UUID

from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.api.dino_api import DinoApi
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos.tamed_dino import TamedDino
from arkparse.logging import ArkSaveLogger
from arkparse.object_model.ark_game_object import ArkGameObject

# save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.ABERRATION).download_save_file(Path.cwd()) # download the save file from an FTP server
save_path = Path.cwd() / "Aberration_WP.ark"                                                                    # Or use a local path

looking_for: str = "SuperSpyglass"
save = AsaSave(save_path) 
   
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

    
