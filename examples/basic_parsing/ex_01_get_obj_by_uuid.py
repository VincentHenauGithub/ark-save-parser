from pathlib import Path
from uuid import UUID

from arkparse.saves.asa_save import AsaSave
from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.object_model.cryopods.cryopod import Cryopod 
from arkparse.logging import ArkSaveLogger

# retrieve the save file (can also retrieve it from a local path)
# save_path = ArkFtpClient.from_config(
#     Path("../../ftp_config.json"), ArkMap.ABERRATION).download_save_file(Path.cwd())
save_path = Path("C:\\data\\personal\\git\\ark-save-parser\\tests\\test_data\\set_1\\Ragnarok_WP\\Ragnarok_WP.ark")  # Example local path
save = AsaSave(save_path)

# Get object by UUID
# ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.PARSER, True)
uuid = UUID("faa89ebf-6fe1-9b45-8e5e-77f3b92d48d4")         # Example UUID
# obj: ArkGameObject = save.get_game_object_by_id(
#     uuid)       # Create generic Ark object

cryo = Cryopod(uuid, save)
