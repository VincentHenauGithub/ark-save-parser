from pathlib import Path

from arkparse.utils import draw_heatmap
from arkparse.api.dino_api import DinoApi
from arkparse.enums import ArkMap, ArkStat
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos.tamed_dino import Dino
from arkparse.classes.dinos import Dinos
from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap


save_path = Path.cwd() / "test_saves" / "server.ark" # replace with path to your save file

# Or get your save file from an FTP server
map = ArkMap.LOST_COLONY # replace with your map
save_path  = ArkFtpClient.from_config("../../ftp_config.json", map).download_save_file(Path.cwd()) 

save = AsaSave(save_path)   # load the save file
dino_api = DinoApi(save)    # create a DinoApi object

limit = 25 # set the limit for the stats
dinos = dino_api.get_all_filtered(# only consider wild dinos
                                  tamed=False, 
                                  # set the stat limit
                                  stat_minimum=limit,
                                  # filter the type of dino you want to track
                                  class_names=[Dinos.trike],
                                  # only consider dinos up to level 150 (no wild wyverns / drakes)
                                  level_upper_bound=150,
                                  # only consider dinos with at least 'limit' points in the configured stats (if not assigned, all stats are considered)
                                  stats=[ArkStat.HEALTH, ArkStat.MELEE_DAMAGE])                 


print(f"Found {len(dinos)} dinos matching the criteria") # print how many dinos were found

# print the output
for key, dino in dinos.items():
    dino : Dino = dino
    s = f"{dino}: {dino.location.as_map_coords(map)}"
    stats = dino.stats.get_of_at_least(limit)
    for stat in stats:
        s += f" {dino.stats.stat_to_string(stat)}"
    print(s) # print the dino's name, location, and stats above the limits

# example print output:
# Dino(type=Arthro_Character_BP_Aberrant, lv=135): (92.06, 69.56) melee_damage=35
# Dino(type=Dimorph_Character_BP_Aberrant, lv=140): (60.96, 41.45) health=35
# Dino(type=Arthro_Character_BP_Aberrant, lv=140): (91.97, 50.07) melee_damage=36
# Dino(type=Arthro_Character_BP_Aberrant, lv=150): (82.31, 68.03) health=39 food=35 melee_damage=35

heatmap = dino_api.create_heatmap(dinos=dinos, map=map) # create a heatmap of the dinos
draw_heatmap(heatmap, map)                              # draw the heatmap for the selected map