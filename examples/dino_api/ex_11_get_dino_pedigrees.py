from typing import Dict, List
from uuid import UUID
from pathlib import Path
import random

from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.api import DinoApi, PlayerApi
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos.pedigree import Pedigree
from arkparse.utils import _TEST_FILE_ASTRAEOS_WP

save_path = _TEST_FILE_ASTRAEOS_WP
save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.RAGNAROK).download_save_file(Path.cwd())
print(f"Loading save file: {save_path}")

save = AsaSave(save_path) # load the save file
dino_api = DinoApi(save) # using the dino API as an example     
player_api = PlayerApi(save) # using the player API as an example   
tamed = dino_api.get_all_tamed()
print(f"Total tamed dinos: {len(tamed)}")

random_tamed = list(tamed.values())[random.randint(0, len(tamed)-1)]


# pedigrees: List[Pedigree] = dino_api.get_all_pedigrees(player_api)
pedigrees: List[Pedigree] = [Pedigree(random_tamed, dino_api, player_api)]

random_pedigree = pedigrees[random.randint(0, len(pedigrees)-1)]

random_pedigree.visualize_as_html(f"random_pedigree_{random_pedigree.dino_type}.html", random_pedigree.dino_type)
random_pedigree.print_tree()

count = 0
for pedigree in pedigrees:
    if pedigree.mixed_ownership:
        print(f"Mixed ownership pedigree found for {pedigree.dino_type}, bottom_ids: {[str(dino.id_) for dino in pedigree.bottom_entries]}")
        pedigree.visualize_as_html(f"mixed_ownership_pedigree_{pedigree.dino_type}_{count}.html", pedigree.dino_type)
        count += 1
