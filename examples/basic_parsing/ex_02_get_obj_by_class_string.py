from pathlib import Path
from typing import Dict
from uuid import UUID

from arkparse.saves.asa_save import AsaSave
from arkparse.api import StructureApi
from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.object_model.structures import StructureWithInventory

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(
    Path("../../ftp_config.json"), ArkMap.RAGNAROK).download_save_file(Path.cwd())
save = AsaSave(save_path)

# Get object by UUID
# Example, can be part of a string or full class string
class_ = ["StorageBox_Large_C", "BP_DedicatedStorage_C", "StorageBox_ChemBench_C", "StorageBox_IndustrialGrinder_C", "StorageBox_Fabricator_C", "StorageBox_TekGenerator_C", "StorageBox_Huge_C", "StorageBox_AnvilBench_C", "StorageBox_TekReplicator_C", "StorageBox_Small_C", "PrimalItemStructure_LibraryStorage_C", "StorageBox_TekReplicator_C", "StorageBox_TekReplicator_C", "StorageBox_TekReplicator_C"]
config = GameObjectReaderConfiguration(
    blueprint_name_filter=lambda name: name is not None and any(cls in name for cls in class_))  # Create filter
# Create list of generic Ark objects

structure_api = StructureApi(save)
storages = structure_api.get_all(config)
print(f"Found {len(storages)} storage boxes on the map")

for key, storage in storages.items():
    # item quantity
    if not isinstance(storage, StructureWithInventory):
        print(f"Storage {storage.get_short_name()} is not a StructureWithInventory")
    else:
        print(f"Storage {storage.get_short_name()} ({storage.uuid})")
        storage: StructureWithInventory = storage
        print(f"Max Quantity: {storage.max_item_count}")
        print(f"Current Quantity: {len(storage.inventory.items) if storage.inventory is not None else 0}")

        print("Items:")
        if storage.inventory is not None:
            for item in storage.inventory.items.values():
                print(f"- {item.get_short_name()} x{item.quantity}")
        else:
            print(" No inventory")
