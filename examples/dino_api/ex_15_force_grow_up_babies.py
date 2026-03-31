from pathlib import Path
from typing import Dict
from uuid import UUID

from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.api.dino_api import DinoApi
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos import TamedBaby, Baby, Dino
from arkparse.classes.dinos import Dinos

save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.LOST_COLONY).download_save_file(Path.cwd()) # or download the save file from an FTP server
# save_path = Path.cwd() / "LostColony_WP.ark" # or load the save file from a local path
save = AsaSave(save_path)  
                                                                                  # load the save file
dino_api = DinoApi(save)                                                                                        # create a DinoApi object

dinos: Dict[UUID, Dino] = dino_api.get_all_babies(include_cryopodded=False)

tamed = dino_api.get_all_tamed()
for dino in tamed.values():
    if dino.owner.imprinter == "Skinny Skank":
        dino.heal()
        print(f"Healed {dino.get_short_name()} owned by {dino.owner.imprinter}")
        # Display details of all babies
        
print("Details of tamed babies:")
for dino in dinos.values():
    if isinstance(dino, TamedBaby) and dino.object.blueprint == Dinos.stegosaurus:
        print(f"Tamed Baby: {dino.get_short_name()}, Stage: {dino.stage.value}, Matured: {dino.percentage_matured:.2f}%, owner: {dino.owner}")
        dino.grow_up(100.0)
        dino.wake_up()

save.store_db(Path.cwd() / "LostColony_WP.ark") # store the updated save file

# check the changes
new_save = AsaSave(Path.cwd() / "LostColony_WP.ark")
new_dino_api = DinoApi(new_save)
new_dinos: Dict[UUID, Dino] = new_dino_api.get_all_babies(include_cryopodded=False)
print("\nDetails of tamed babies after growing up:")
for dino in new_dinos.values():
    if isinstance(dino, TamedBaby) and dino.object.blueprint == Dinos.stegosaurus:
        print(f"Tamed Baby: {dino.get_short_name()}, Stage: {dino.stage.value}, Matured: {dino.percentage_matured:.2f}%, owner: {dino.owner}")

ArkFtpClient.from_config('../../ftp_config.json', ArkMap.LOST_COLONY).upload_save_file(Path.cwd() / "LostColony_WP.ark", map=ArkMap.LOST_COLONY) # upload the modified save file back to the FTP server
