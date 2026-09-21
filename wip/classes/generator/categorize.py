"""Assigns every vanilla blueprint path to exactly one generated module.

The dump files written by ``get_all_class_names.py`` categorise on substrings of
the full path, which is leaky (``Ammonite_Character`` lands in ``ammo.txt``).
Here we key off the class name prefix instead -- that is what ARK actually uses
to denote an asset's kind -- and fall back to the path only for the structure
meshes that carry no prefix at all.

Every vanilla class lands in exactly one bucket: nothing is dropped, so a save
parsed against the generated modules leaves an empty uncategorized dump.
"""

from naming import leaf_of

# Dino AI is spelled four different ways across the DLCs.
AI_MARKERS = ("_AIController", "_AI_Controller", "_AI_Blueprint", "_AIBlueprint")

# Leaf names that are structures but carry none of the usual Structure prefixes.
LOOSE_STRUCTURES = ("BP_DoubleDoor", "BP_DedicatedStorage", "BP_Ship", "BP_LevelStructure",
                    "PortableRope_Ladder", "Underwater_Gate", "BearTrap_", "Flag_SM")

# (category, predicate) in priority order -- the first match wins.
RULES = [
    # --- dino side ---------------------------------------------------------
    ("dino_ai", lambda leaf, path: any(m in leaf for m in AI_MARKERS)
     or leaf.endswith("_AI")),
    ("dino_status", lambda leaf, path: "DinoCharacterStatusComponent" in leaf
     or leaf.startswith("DinoCharacterStatus_BP")),
    ("dino_harvesting", lambda leaf, path: leaf.startswith("DinoDeathHarvestingComponent")
     or leaf.endswith("HarvestComponent")),
    ("dino_inventory", lambda leaf, path: leaf.startswith("Dino")
     and ("InventoryComponent" in leaf or leaf.startswith("DinoTamedInventory"))),
    ("dinos", lambda leaf, path: "_Character_BP" in leaf or "_Char_BP" in leaf
     or leaf.endswith("_Character") or ("_Character" in leaf and leaf.endswith("_BP"))),

    # --- items, keyed on the PrimalItem<Kind> prefix -----------------------
    ("dyes", lambda leaf, path: leaf.startswith("PrimalItemDye")),
    ("resources", lambda leaf, path: leaf.startswith("PrimalItemResource")),
    ("consumables", lambda leaf, path: leaf.startswith("PrimalItemConsumable")),
    ("ammo", lambda leaf, path: leaf.startswith("PrimalItemAmmo")),
    ("trophies", lambda leaf, path: leaf.startswith("PrimalItemTrophy")),
    ("artifacts", lambda leaf, path: leaf.startswith("PrimalItemArtifact")),
    ("costumes", lambda leaf, path: leaf.startswith("PrimalItemCostume")),
    ("skins", lambda leaf, path: leaf.startswith("PrimalItemSkin")),
    ("structure_skins", lambda leaf, path: leaf.startswith("PrimalItemStructureSkin")),
    ("structure_items", lambda leaf, path: leaf.startswith("PrimalItemStructure")),
    ("saddles", lambda leaf, path: leaf.startswith("PrimalItemArmor")
     and ("Saddle" in leaf or "/Saddle" in path)),
    ("armor", lambda leaf, path: leaf.startswith("PrimalItemArmor")),
    ("weapons", lambda leaf, path: leaf.startswith("PrimalItemWeapon")
     or leaf.startswith("Weap")),
    ("misc_items", lambda leaf, path: leaf.startswith("PrimalItem") or "_Item_" in leaf),

    # --- rideable things that are neither dino nor structure ---------------
    ("vehicles", lambda leaf, path: leaf.startswith(("Raft_BP", "MotorRaft_BP", "Car_Vehicle",
                                                     "BrigShip", "SloopShip"))
     or "Zeppelin" in leaf),

    # --- world side --------------------------------------------------------
    ("inventories", lambda leaf, path: leaf.startswith("PrimalInventory")),
    ("buffs", lambda leaf, path: leaf.startswith(("Buff", "PrimalBuff"))),
    ("drops", lambda leaf, path: leaf.startswith(("DroppedItem", "SupplyCrate",
                                                  "ArtifactCrate", "ElementWall_Horde"))
     or leaf.endswith("Nest")),
    ("world", lambda leaf, path: leaf.startswith(("BossArenaManager", "MissionManager",
                                                  "MissionDispatcher", "NPCZoneManager",
                                                  "DayCycleManager", "GasVein", "BP_Hero"))
     or "DayCycle" in leaf),
    ("structures", lambda leaf, path: leaf.startswith(("StructureBP", "PrimalStructure",
                                                       "Structure", "StairSM"))
     or leaf.startswith(LOOSE_STRUCTURES) or "TributeTerminal" in leaf
     or "Structure" in leaf
     or "/Structures/" in path or "/Structure/" in path
     or "/Furniture/" in path),
]


def categorize(path: str) -> str:
    leaf = leaf_of(path)
    for name, matches in RULES:
        if matches(leaf, path):
            return name
    return "misc"


def group_all(paths):
    """Return ``{category: [paths]}`` covering every input path."""
    out = {}
    for path in paths:
        out.setdefault(categorize(path), []).append(path)
    return out
