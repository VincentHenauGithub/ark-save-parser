"""Shared helpers for turning ARK blueprint paths into readable python identifiers.

The generated modules under ``src/arkparse/classes`` follow one shape::

    class <Group>:
        <attribute>: str = "<blueprint path>"

        all_bps = [<attribute>, ...]

so every generator only has to answer two questions per blueprint path:
which group does it belong to, and what should the attribute be called.
"""

import keyword
import re

# Tokens that carry no meaning in an attribute name; they are the generic
# "this is a blueprint" prefixes ARK puts on nearly every class.
NOISE_PREFIXES = (
    "PrimalItemStructureSkin_",
    "PrimalItemStructure_",
    "PrimalItemConsumable_",
    "PrimalItemResource_",
    "PrimalItemCostume_",
    "PrimalItemArmor_",
    "PrimalItemAmmo_",
    "PrimalItemWeapon_",
    "PrimalItemSkin_",
    "PrimalItemDye_",
    "PrimalItemTrophy_",
    "PrimalItemArtifact_",
    "PrimalItemArtifactSE_",
    "PrimalItemArtifactAB_",
    "PrimalItemCraftable_",
    "PrimalItem_",
    "PrimalItem",
    "PrimalInventoryBP_",
    "PrimalInventory_",
    "StructureBP_",
    "StructureSM_",
    "Structure_",
    "BP_",
    "SM_",
)

# Mixed-case abbreviations the CamelCase splitter would otherwise tear apart
# (``ToF`` -> ``to_f``). Normalising them to all-caps keeps them one token.
ACRONYMS = ("ToF", "XP", "VR")


def strip_noise(leaf: str) -> str:
    """Drop the repetitive ``PrimalItemX_`` / ``StructureBP_`` style prefixes."""
    for prefix in NOISE_PREFIXES:
        if leaf.startswith(prefix):
            return leaf[len(prefix):]
    return leaf


def split_words(text: str):
    """Split ``GarageDoor_Small_V`` into ``['Garage', 'Door', 'Small', 'V']``."""
    words = []
    for chunk in re.split(r"[_\-\s]+", text):
        if not chunk:
            continue
        for acronym in ACRONYMS:
            chunk = chunk.replace(acronym, acronym.upper())
        # Break CamelCase, but keep runs of capitals (TEK, ASA) and the digits
        # that tier names attach to them (T0, T3, Mk2) as single words.
        words.extend(re.findall(r"[A-Z]+\d*(?![a-z])|[A-Z][a-z]*\d*|\d+|[a-z]+\d*", chunk))
    return words


def snake(text: str) -> str:
    """Readable snake_case identifier for a blueprint name fragment."""
    words = [w.lower() for w in split_words(text)]
    if not words:
        return "unnamed"
    name = "_".join(words)
    name = re.sub(r"_+", "_", name).strip("_")
    if name[0].isdigit():
        name = "_" + name
    if keyword.iskeyword(name):
        name += "_"
    return name


def leaf_of(path: str) -> str:
    """``/Game/.../PrimalItemDye_Red_1_Ruby.PrimalItemDye_Red_1_Ruby_C`` -> leaf name."""
    return path.rsplit("/", 1)[-1].split(".", 1)[0]


def attr_name(path: str) -> str:
    """Default attribute name: the leaf with its noise prefix removed, snake_cased."""
    return snake(strip_noise(leaf_of(path)))


def resolve_names(entries, taken=()):
    """Give every ``(name, path)`` entry an attribute name unique within a class.

    A clash first falls back to the blueprint's own class name, which is unique
    by construction and still readable (``doorframe`` -> ``doorframe_short_stone``);
    only if that is taken too does a numeric suffix appear.
    """
    used = set(taken)
    out = []
    for name, path in entries:
        if name in used:
            name = snake(re.sub(r"^PrimalItem", "", leaf_of(path)))
        candidate, n = name, 1
        while candidate in used:
            n += 1
            candidate = f"{name}_{n}"
        used.add(candidate)
        out.append(candidate)
    return out
