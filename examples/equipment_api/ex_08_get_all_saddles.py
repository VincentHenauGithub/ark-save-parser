from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse import AsaSave
from arkparse.api import DinoApi, EquipmentApi
from arkparse.object_model.equipment import Saddle

# Retrieve the save file (can also retrieve it from FTP).
save_path = Path("C:/Users/Shadow/Documents/TheIsland/TheIsland_WP.ark")
# Load save file.
save = AsaSave(save_path)
# Initialize equipment API.
equipment_api = EquipmentApi(save)
# Initialize dino API.
dino_api = DinoApi(save)

# Get saddles from items.
saddles_from_items: Dict[UUID, Saddle] = equipment_api.get_saddles()

# Get saddles from cryopods.
saddles_from_cryopods: Dict[UUID, Saddle] = dino_api.get_saddles_from_cryopods()

# Merge found saddles.
all_saddles: Dict[UUID, Saddle] = saddles_from_items | saddles_from_cryopods

# Log all saddles.
for key, saddle in all_saddles.items():
    print(saddle)

print(f"Found {len(saddles_from_items)} saddles in items")
print(f"Found {len(saddles_from_cryopods)} saddles in cryopods")
print(f"Found {len(all_saddles)} saddles in total")
