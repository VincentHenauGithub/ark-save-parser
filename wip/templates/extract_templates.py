"""Pick and write the template object for each item archetype.

Run against a save that is rich in content::

    python extract_templates.py <save.ark> ../../src/arkparse/assets/templates report.json


A template has to be the *maximal* variant of its archetype: every write in the
library is replace_*(property, value), so a property missing from the template
can never be set afterwards. Inventories and plain items are the exception --
there the minimal shape is what generalises.
"""
import sys, json, re, collections
from pathlib import Path
sys.path.insert(0, "src")
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase

SPOIL = {"NextSpoilingTime", "LastSpoilingTime", "CreationTime"}
CRAFT = {"CrafterCharacterName", "CrafterTribeName", "CraftedSkillBonus", "CraftingSkill"}
COLOR = {"ItemColorID", "CustomColors"}
RECIPE = {"CustomItemID", "CustomItemName", "CustomItemDescription", "CustomResourceRequirements"}
GEAR = {"ItemStatValues", "ItemRating", "ItemQualityIndex"}
CRAFTQ = {"CraftQueue", "NextCraftCompletionTime"}

# name: (family pattern, must have, must not have, nice to have, minimise?)
ARCH = {
 "cryopod": (r"Cryopod", {"AssociatedDinoID1", "AssociatedDinoID2", "CustomItemDatas"},
             set(), SPOIL | {"SavedDurability"}, False),
 "fertilized_egg": (r"Egg|Embryo", {"EggNumberOfLevelUpPointsApplied", "EggDinoAncestors"},
                    set(), SPOIL | {"SavedDurability", "ItemRating", "CustomItemDatas",
                                    "EggColorSetIndices", "EggGenderOverride"}, False),
 "custom_recipe": (r"CustomFoodRecipe|CustomDrinkRecipe", {"CustomItemID", "CustomItemName"},
                   set(), RECIPE | COLOR | CRAFT | SPOIL | {"ItemQuantity"}, False),
 "skin": (r"PrimalItemSkin|PrimalItemCostume", {"ItemColorID", "CustomItemDatas"},
          GEAR - {"ItemQualityIndex"}, COLOR | SPOIL | {"ItemQualityIndex", "SavedDurability"}, False),
 "stackable_spoiling": (r"PrimalItemConsumable|PrimalItemResource",
                        {"ItemQuantity", "NextSpoilingTime"}, GEAR - {"ItemQualityIndex"} | RECIPE,
                        SPOIL | CRAFT | {"ItemQualityIndex"}, False),
 "tool": (r"PrimalItem_Weapon|PrimalItemConsumable|PrimalItemStructure",
          {"SavedDurability", "NextSpoilingTime"}, GEAR | {"CustomItemDatas"} | RECIPE,
          SPOIL | CRAFT, False),
 "simple": (r"PrimalItemTrophy|PrimalItemArtifact|PrimalItem_Note|PrimalItemDye",
            {"ItemID", "OwnerInventory", "ItemVersion"},
            GEAR | SPOIL | CRAFT | COLOR | RECIPE | CRAFTQ |
            {"ItemQuantity", "SavedDurability", "CustomItemDatas", "AssociatedDinoID1"}, set(), True),
 "inventory_with_item": (r"PrimalInventory", {"InventoryItems", "bInitializedMe"},
                         {"ItemSlots", "SortingInputs", "CraftQueue"}, set(), True),
 "inventory_empty": (r"PrimalInventory", {"bInitializedMe", "LastInventoryRefreshTime"},
                     {"InventoryItems", "ItemSlots", "SortingInputs", "CraftQueue"}, set(), True),
}

save = AsaSave(Path(sys.argv[1]))
out_dir = Path(sys.argv[2])
best = {}
for u, o in save.get_game_objects().items():
    short = o.blueprint.rsplit("/", 1)[-1].split(".")[0]
    try:
        names = [p.name for p in o.properties]
    except Exception:
        continue
    have = set(names)
    for arch, (pattern, must, mustnot, nice, minimise) in ARCH.items():
        if not re.search(pattern, short) or not must <= have or (mustnot & have):
            continue
        # Prefer vanilla content: a mod class in a template leaks that name
        # into the name table of every save generated from it.
        score = (o.blueprint.startswith("/Game/"),
                 len(nice & have), -len(have) if minimise else len(have))
        if arch not in best or score > best[arch][0]:
            best[arch] = (score, u, o.blueprint, sorted(collections.Counter(names).items()))

report = {}
for arch, (_, u, bp, props) in best.items():
    obj = ParsedObjectBase(u, save)
    sub, name = arch.split("_", 1) if arch.startswith("inventory_") else ("item", arch)
    target = out_dir / ("inventory" if sub == "inventory" else "item")
    obj.store_binary(target, name=name, prefix="", no_suffix=True)
    report[arch] = {"blueprint": bp, "file": f"{target.name}/{name}",
                    "props": [n for n, _ in props]}
    print(f"{arch:22s} {bp.rsplit('/',1)[-1].split('.')[0]:44s} {sum(c for _, c in props):3d} props")
Path(sys.argv[3]).write_text(json.dumps(report, indent=1))
print("MISSING:", sorted(set(ARCH) - set(best)))

# The header ints insert_array() needs when adding InventoryItems to an
# inventory that has none.
_, u, bp, _ = best["inventory_with_item"]
obj = ParsedObjectBase(u, save)
pos = obj.binary.set_property_position("InventoryItems")
obj.binary.set_position(pos + 16)
print("InventoryItems header: dup_index=", obj.binary.read_uint32(), end=" ")
obj.binary.set_position(pos + 28)
print("type_int=", obj.binary.read_uint32(), "array_len=", obj.binary.read_uint32())
