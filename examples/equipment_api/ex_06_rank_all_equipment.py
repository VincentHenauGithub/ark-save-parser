from pathlib import Path
from uuid import UUID
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

from arkparse import AsaSave
from arkparse.enums import ArkMap, ArkItemQuality
from arkparse.ftp.ark_ftp_client import ArkFtpClient
from arkparse.api.equipment_api import EquipmentApi
from arkparse.object_model.equipment.__equipment import Equipment
from arkparse.object_model.equipment import Weapon, Armor, Saddle, Shield

# retrieve the save file (can also retrieve it from a local path)
# save_path = ArkFtpClient.from_config(
#     Path("../../ftp_config.json"), ArkMap.ABERRATION).download_save_file(Path.cwd())
save_path = store_path = Path("D:\\SteamLibrary\\steamapps\\common\\ARK Survival Ascended\\ShooterGame\\Saved\\SavedArksLocal\\Ragnarok_WP\\Ragnarok_WP.ark")
save = AsaSave(save_path)

equipment_api = EquipmentApi(save)  # Create Equipment API

weapons: Dict[UUID, Weapon] = equipment_api.get_all(EquipmentApi.Classes.WEAPON)
armors: Dict[UUID, Armor] = equipment_api.get_all(EquipmentApi.Classes.ARMOR)
shields: Dict[UUID, Shield] = equipment_api.get_all(EquipmentApi.Classes.SHIELD)
saddles: Dict[UUID, Saddle] = equipment_api.get_all(EquipmentApi.Classes.SADDLE)

ratings = {}
for d in [weapons, armors, shields, saddles]:
    d: Dict[UUID, Equipment]
    for key, value in d.items():
        print(value)
        value: Equipment
        ratings[key] = [type(value), value.rating, value.get_average_stat(), ArkItemQuality(value.quality), value.is_bp]


# Convert to a Pandas DataFrame
data = []
for key, (eq_type, rating, avg_stat, quality, is_bp) in ratings.items():
    data.append({
        'Type': eq_type.__name__,
        'Rating': rating,
        'Average Stat': avg_stat,
        'Quality': quality.name,
        'Is_BP': is_bp
    })

df = pd.DataFrame(data)

# Mapping equipment classes to marker shapes
shape_dict = {
    'Weapon': 'o',   # Circle
    'Armor': 's',    # Square
    'Shield': '^',   # Triangle Up
    'Saddle': 'D'    # Diamond
}

# Mapping equipment qualities to ARK colors
quality_color_map = {
    'PRIMITIVE': '#808080',
    'RAMSHACKLE': '#11b843',
    'APPRENTICE': '#1044b4',
    'JOURNEYMAN': '#80097a',
    'MASTERCRAFT': '#c2b503',   
    'ASCENDANT': '#1fe7bc'    
}

# Create Scatter Plot
def create_scatter_plot(dataframe, title):
    plt.figure(figsize=(12, 8))
    
    # Iterate over each equipment class to plot separately for shape differentiation
    for eq_class, marker in shape_dict.items():
        subset = dataframe[dataframe['Type'] == eq_class]
        plt.scatter(
            subset['Rating'],
            subset['Average Stat'],
            marker=marker,
            c=subset['Quality'].map(quality_color_map),
            label=eq_class,
            edgecolors='w',
            s=100,
            alpha=0.7
        )
    
    plt.xlabel('Rating', fontsize=14)
    plt.ylabel('Average Stat', fontsize=14)
    plt.title(title, fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Create legend for Equipment Classes
    class_handles = [
        Line2D([0], [0], marker=marker, color='w', label=cls,
               markerfacecolor='gray', markersize=10, markeredgecolor='w')
        for cls, marker in shape_dict.items()
    ]
    
    # Create legend for Equipment Qualities
    quality_handles = [
        Line2D([0], [0], marker='o', color='w', label=quality,
               markerfacecolor=color, markersize=10)
        for quality, color in quality_color_map.items()
    ]

    first_legend = plt.legend(handles=class_handles, title='Equipment Class', loc='upper left')
    plt.legend(handles=quality_handles, title='Equipment Quality', loc='lower right')
    plt.gca().add_artist(first_legend)
    
    plt.tight_layout()
    plt.show()

# Plot All Equipment
create_scatter_plot(df, 'All Equipment: Rating vs. Average Stat')

# Plot Blueprints Only
bp_df = df[df['Is_BP'] == True]
create_scatter_plot(bp_df, 'Blueprints Only: Rating vs. Average Stat')

 