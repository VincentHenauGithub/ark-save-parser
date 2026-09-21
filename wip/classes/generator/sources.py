"""Loads the raw class dumps produced by ``get_all_class_names.py``."""

from pathlib import Path

UNCATEGORIZED = Path(__file__).resolve().parent.parent / "uncategorized"

# Only vanilla + official DLC content lands in the core library; everything a
# server happens to have installed stays in the uncategorized dump.
VANILLA_PREFIX = "/Game/"


def load(category: str):
    """Sorted vanilla blueprint paths for one dump file (without the .txt)."""
    path = UNCATEGORIZED / f"{category}.txt"
    lines = path.read_text().splitlines()
    return sorted({line.strip() for line in lines
                   if line.strip().startswith(VANILLA_PREFIX)})
