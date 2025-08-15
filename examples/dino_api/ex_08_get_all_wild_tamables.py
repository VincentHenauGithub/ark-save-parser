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
wild_tamables_diff10: Dict[UUID, Dino] = dino_api.get_all_wild_tamables(360, 300)
wild_dinos: Dict[UUID, Dino] = dino_api.get_all_wild()

wild_tamables_filtered = 0
wild_tamables_diff10_filtered = 0
for dino in wild_dinos.values():
    if is_tamable(dino):
        wild_tamables_filtered+=1

    if is_tamable(dino, 360, 300):
        wild_tamables_diff10_filtered+=1

print(f"Total Wild Dinos: {len(wild_dinos)}")

# Results should be same
print(f"Total Wild Tamables (default difficult): >>{len(wild_tamables)}<< should be equal to >>{wild_tamables_filtered}<<")

# Results should be same
print(f"Total Wild Tamables (10x difficult): >>{len(wild_tamables_diff10)}<< should be equal to >>{wild_tamables_diff10_filtered}<<")