from pathlib import Path
from typing import Dict
from uuid import UUID

from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.api.dino_api import DinoApi
from arkparse.enums import ArkMap, ArkDinoTrait
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos.tamed_dino import TamedDino
from arkparse.logging import ArkSaveLogger
from arkparse.parsing import ArkBinaryParser
from arkparse.object_model.ark_game_object import ArkGameObject

save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.ABERRATION).download_save_file(Path.cwd()) # or download the save file from an FTP server
save = AsaSave(save_path)                                                                                       # load the save file
dino_api = DinoApi(save)                                                                                        # create a DinoApi object

dinos: Dict[UUID, TamedDino] = dino_api.get_all_tamed()
dino = list(dinos.values())[0] # Get a random dino

dino.clear_gene_traits(save)                            # Remove all traits
dino.add_gene_trait(ArkDinoTrait.AGGRESSIVE, 0, save)   # Add a trait (of level 0)
dino.add_gene_trait(ArkDinoTrait.ANGRY, 0, save)        # Add another trait (of level 0)
dino.remove_gene_trait(ArkDinoTrait.ANGRY, save)        # Remove a trait
dino.clear_gene_traits(save)                            # Remove all traits                                     
dino.add_gene_trait(ArkDinoTrait.COWARDLY, 1, save)     # Add a trait (of level 1)

# Update the binary in the database
save.store_db(Path.cwd() / "new_Aberration_WP.ark")
