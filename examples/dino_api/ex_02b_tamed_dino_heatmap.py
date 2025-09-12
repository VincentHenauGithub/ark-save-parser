from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse.utils import draw_heatmap
from arkparse.api.dino_api import DinoApi, TamedDino, MapCoords
from arkparse.logging import ArkSaveLogger
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave
from arkparse.ftp.ark_ftp_client import ArkFtpClient


def ex_02b_tamed_dino_heatmap(save_path: Path, map: ArkMap) -> None:
    save = AsaSave(save_path)                               # load the save file
    dino_api = DinoApi(save)                                # create a DinoApi object

    dinos: Dict[UUID, TamedDino] = dino_api.get_all_tamed(False)

    for dino in dinos.values():                  # iterate over all dinos
        ArkSaveLogger.info_log(f"{dino.get_short_name()} (lv {dino.stats.current_level}, name: {dino.tamed_name}) owned by {dino.owner.tamer_string} at {dino.location.as_map_coords(ArkMap.RAGNAROK)}")  # print owner, name, species, level, and location
        if dino.object.get_property_value("DinoAncestors") is not None:
            print(dino.object.get_property_value("DinoAncestors"))
            print(dino.object.get_property_value("DinoAncestorsMale"))
            # dino.object.print_properties()
            print(len(dino.object.get_property_value("DinoAncestors") or []))
            print(len(dino.object.get_property_value("DinoAncestorsMale") or []))

    # heatmap = dino_api.create_heatmap(map=map, dinos=dinos)          # create a heatmap of the dinos
    # draw_heatmap(heatmap, map)                # draw the heatmap for the Aberration map

if __name__ == "__main__":
    # save_path = ArkFtpClient.from_config('../../ftp_config.json', ArkMap.ABERRATION).download_save_file(Path.cwd())
    save_path = Path.cwd() / "Ragnarok_WP.ark"
    ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.WARNING, False)
    ex_02b_tamed_dino_heatmap(save_path, ArkMap.RAGNAROK)  # run the example