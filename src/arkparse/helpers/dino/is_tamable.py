from pathlib import Path
from importlib.resources import files

package = 'arkparse.assets'
with open(files(package) / f'tamable_dinos.txt', 'r', encoding='utf-8') as f:
    TAMABLE_CLASSNAMES = set(line.strip() for line in f if line.strip())

def is_tamable(dino, max_tek_level=180, max_level=150) -> bool:
    dino_class = dino.get_short_name() + "_C"
    lvl = int(getattr(dino.stats, "base_level", 0))

    # Corrupt dinos are not tamable
    if "_Corrupt" in dino_class:
        return False

    # Bionic (TEK) dinos max level check
    if "Bionic" in dino_class and lvl > max_tek_level:
        return False

    # Non-TEK dinos max level check
    if "Bionic" not in dino_class and lvl > max_level:
        return False

    return dino_class in TAMABLE_CLASSNAMES