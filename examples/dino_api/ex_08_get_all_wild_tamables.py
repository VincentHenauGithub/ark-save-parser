from pathlib import Path
from typing import Dict
from uuid import UUID

from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.api.dino_api import DinoApi
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos import Dino
from arkparse.helpers.dino.is_tamable import is_tamable

save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.RAGNAROK).download_save_file(Path.cwd())   # or download the save file from an FTP server
save = AsaSave(save_path)                                                                                       # load the save file
dino_api = DinoApi(save)                                                                                        # create a DinoApi object

wild_tamables: Dict[UUID, Dino] = dino_api.get_all_wild_tamables()
wild_dinos: Dict[UUID, Dino] = dino_api.get_all_wild()

wild_tamables_filtered = []
for dino in wild_dinos.values():
    if not is_tamable(dino):
        continue

    wild_tamables_filtered.append(dino)

print(f"Total Wild Dinos: {len(wild_dinos)}")
print(f"Total Wild Tamables: {len(wild_tamables)}")
print(f"Total Wild Tamables (after filtering): {len(wild_tamables_filtered)}")