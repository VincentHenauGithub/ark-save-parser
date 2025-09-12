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

save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.ABERRATION).download_save_file(Path.cwd()) # download the save file from an FTP server
save_path = Path.cwd() / "Aberration_WP.ark"                                                                    # Or use a local path

save = AsaSave(save_path)                                                                                       # load the save file
dino_api = DinoApi(save) # using the dino API as an example               
dinos: Dict[UUID, TamedDino] = dino_api.get_all_tamed()


# Get a random dino
dino = list(dinos.values())[0]

# Print the positions of all names in the dino binary
dino.binary.find_names()

# Print the definitions of all properties in the dino binary by re parsing the object
dino_object = ArkGameObject(dino.object.uuid, dino.object.blueprint, save)
