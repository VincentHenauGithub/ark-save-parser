from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse import AsaSave, Classes
from arkparse.api import StructureApi
from arkparse.ftp import ArkFtpClient
from arkparse.enums import ArkMap
from arkparse.utils import draw_heatmap
from arkparse.object_model.structures import Structure

map = ArkMap.LOST_COLONY
# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(Path("../../ftp_config.json"), map).download_save_file(Path.cwd())
save = AsaSave(save_path)

min_in_section = 5

structure_api = StructureApi(save)
all_structures: Dict[UUID, Structure] = structure_api.get_all()
print(len(all_structures))
heatmap = structure_api.create_heatmap(structures=all_structures, min_in_section=min_in_section, map=map)
 
# draw the heatmap
draw_heatmap(heatmap, map)