"""What each generated module contains, and how its blueprints are grouped.

``MODULES`` are written whole; ``EXTENSIONS`` are appended into modules that
already exist and are hand-curated. In both cases ``rules`` is an ordered list
of ``(ClassName, markers)``: a blueprint joins the first class one of whose
markers appears in its class name, and the markers are stripped from the
attribute name afterwards. Anything no rule claims goes to ``fallback``.

Grouping is always by what a blueprint *is* -- material, slot, purpose -- never
by which map or DLC it shipped with.
"""

from naming import snake


def dye_name(leaf):
    """``PrimalItemDye_Azure_4_Azure`` -> ``azure``; ``..._Misc_7`` -> ``misc_7``."""
    parts = leaf.removeprefix("PrimalItemDye_").split("_")
    tail = parts[2:] if len(parts) > 2 and parts[1].isdigit() else parts
    return snake("_".join(tail))


# A derived name is occasionally worse than the one a human would pick; those
# are listed here by class name rather than special-cased in the rules.
RENAMES = {
    "PrimalItemArmor_ForSBear": "spirit_bear_saddle",
    "PrimalItemArmor_GrandTortugar_Platform": "grand_tortuga_platform",
}


# Structure assets are spelled SM_ (static mesh), BP_ (blueprint) or
# Structure_ depending on the era they were made in; none of that says what the
# structure is.
STRUCTURE_NOISE = ("SM", "BP", "Structure")


# Building materials, shared by placed structures and the items that place them.
# Order matters: the first material found in a name wins.
MATERIALS = [
    ("Adobe", ("Adobe",)),
    ("Greenhouse", ("Greenhouse",)),
    ("Stone", ("Stone",)),
    ("Metal", ("Metal",)),
    ("Wood", ("Wood", "Wooden")),
    ("Thatch", ("Thatch",)),
    ("Tek", ("Tek",)),
]

# What a structure is for, once its material has been ruled out.
STRUCTURE_ROLES = [
    ("Turrets", ("Turret",)),
    ("TributeTerminals", ("TributeTerminal", "Terminal")),
    ("Water", ("WaterPipe", "WaterTank", "Irrigation", "Aqueduct")),
    ("Crafting", ("Forge", "Bench", "Fabricator", "CookingPot", "Grill", "Campfire",
                  "Mortar", "Compost", "Cauldron", "Smithy", "Loom", "Refinery",
                  "Incubator", "Infuser", "Grinder", "PreservingBin", "Windmill")),
    ("Traps", ("BearTrap", "AlarmTrap", "PoisonTrap", "Snare", "Leash", "Pitfall")),
    ("Halloween", ("Gravestone", "Tombstone", "Pumpkin", "Coffin", "Skull", "Cobweb")),
    ("Christmas", ("Xmas", "Christmas", "Wreath", "Snowman", "Gingerbread")),
    ("Missions", ("Mission", "Outpost", "Defend")),
    ("Taxidermy", ("Taxidermy",)),
    ("Flags", ("Flag",)),
    ("Signs", ("Sign", "Billboard")),
    ("Lights", ("Light", "Lamp", "Torch", "Chandelier", "Sconce", "Candle")),
    ("Storage", ("StorageBox", "Container", "Vault", "Cupboard", "Locker", "Chest",
                 "DedicatedStorage", "Box")),
    ("Furniture", ("Furniture", "Chair", "Table", "Desk", "Couch", "Bed", "Rug",
                   "Shelf", "Stool", "Sofa", "Cabinet", "Hammock")),
    ("Plants", ("PlantSpecies", "CropPlot", "Plant", "Crop")),
    ("Ships", ("Ship", "Raft", "Boat")),
    ("Displays", ("TrophyBase", "TrophyWall", "FishMount", "DisplayCase", "SharkJaws",
                  "PaintingCanvas", "Mirror")),
    ("Elevators", ("Elevator",)),
]

# Every dino asset carries the same boilerplate -- Rex_Character_BP,
# DinoCharacterStatusComponent_BP_Rex, Rex_AIController_BP -- which says what
# kind of asset it is, not which creature. The class it lives in already says
# that, so it is stripped from the attribute name.
DINO_NOISE = ("Character", "Char", "BP")

COMPONENT_NOISE = DINO_NOISE + (
    "DinoCharacterStatusComponent", "DinoCharacterStatus", "DinoTamedInventoryComponent",
    "DinoTamedInventory", "DinoDeathHarvestingComponent", "AIController", "AI",
    "Controller", "Blueprint", "Component",
)


# Which body slot a cosmetic covers.
SKIN_SLOTS = [
    ("Hats", ("Hat", "Helmet", "Mask", "Goggles", "Crown", "Antlers", "Tiara", "Visor")),
    ("Shirts", ("Shirt", "Chest", "Jacket")),
    ("Pants", ("Pants", "Bottoms", "Leggings")),
    ("Boots", ("Boots", "Shoes")),
    ("Gloves", ("Gloves", "Gauntlets")),
    ("Underwear", ("Underwear",)),
    ("WeaponSkins", ("Sword", "Pike", "Spear", "Bow", "Rifle", "Pistol", "Shotgun",
                     "Club", "Axe", "Hatchet", "Sickle", "Torch", "Slingshot",
                     "Crossbow", "Whip", "Knife", "Sniper", "Grenade", "Launcher")),
]

MODULES = [
    dict(
        module="dyes",
        aggregate="Dyes",
        header="Craftable dyes, grouped by the colour family they belong to.",
        categories=["dyes"],
        attr=dye_name,
        fallback="Misc",
        rules=[
            ("Azure", ("Azure",)), ("Blue", ("Blue",)), ("Brown", ("Brown",)),
            ("Chartreuse", ("Chartreuse",)), ("Cyan", ("Cyan",)), ("Fuschia", ("Fuschia",)),
            ("Green", ("Green",)), ("Greyscale", ("Greyscale",)), ("Magenta", ("Magenta",)),
            ("Orange", ("Orange",)), ("Red", ("Red",)), ("Spring", ("Spring",)),
            ("Violet", ("Violet",)), ("Yellow", ("Yellow",)), ("Misc", ("Misc",)),
        ],
    ),
    dict(
        module="skins",
        aggregate="Skins",
        header="Cosmetic skins and dino costumes, grouped by set, then by the slot they cover.",
        categories=["skins", "costumes", "structure_skins"],
        fallback="Misc",
        rules=[
            ("Chibis", ("ChibiDino",)),
            ("DinoSkinPacks", ("AAA",)),
            ("WinterWonderland", ("WW_", "Winter", "Xmas", "Christmas", "Gingerbread",
                                  "Sweater", "CandyCane", "Santa", "Cocoa", "Festive",
                                  "Krampus", "Reindeer", "Lolipop", "Cookie", "Stocking")),
            ("FearEvolved", ("FE_", "Halloween", "Witch", "Werewolf", "Zombie",
                             "Scary", "Vampire", "Strawman", "Skeleton")),
            ("TurkeyTrial", ("TT_", "Turkey", "Cornucopia")),
            ("Valentines", ("Vday", "Valentine", "Love", "Lovely", "Heart", "Rose")),
            ("SummerBash", ("Summer", "Hawaiian", "Bounce")),
            ("Easter", ("Easter", "Eggcellent", "Bunny")),
            ("Thralls", ("Thrall",)),
            ("Characters", ("CharacterSkin",)),
            ("BoneCostumes", ("Bone",)),
            ("GhostCostumes", ("Ghost",)),
            ("CorruptedCostumes", ("Corrupted", "Corrupt")),
            ("Tilesets", ("Tileset",)),
        ] + SKIN_SLOTS + [
            # After the slot rules, so the garden rake stays a weapon skin.
            ("Garden", ("Garden", "Flower", "Vase")),
        ],
    ),
    dict(
        module="trophies",
        aggregate="Trophies",
        header="Boss trophies, skeleton trophies and the artifacts used to summon bosses.",
        categories=["trophies", "artifacts"],
        fallback="Bosses",
        rules=[
            ("Skeletons", ("Skeleton",)),
            ("Artifacts", ("Artifact",)),
        ],
    ),
    dict(
        module="structure_items",
        aggregate="StructureItems",
        header="Inventory items that place a structure, grouped by material and then by purpose.",
        categories=["structure_items"],
        fallback="Misc",
        noise=STRUCTURE_NOISE,
        rules=MATERIALS + STRUCTURE_ROLES,
    ),
    dict(
        module="dino_components",
        aggregate="DinoComponents",
        header="Per-species components attached to a dino: stats, inventory, AI and harvest tables.",
        categories=["dino_status", "dino_inventory", "dino_ai", "dino_harvesting"],
        split_by_category=True,
        noise=COMPONENT_NOISE,
        category_classes={
            "dino_status": "StatusComponents",
            "dino_inventory": "InventoryComponents",
            "dino_ai": "AIControllers",
            "dino_harvesting": "HarvestComponents",
        },
    ),
    dict(
        module="items",
        aggregate="Items",
        header="Remaining inventory items, container inventories and buffs.",
        categories=["misc_items", "inventories", "buffs", "misc"],
        fallback="Misc",
        rules=[
            ("ArmorTraits", ("ItemTrait_Armor",)),
            ("GunTraits", ("ItemTrait_Gun",)),
            ("MeleeTraits", ("ItemTrait_Melee",)),
            ("ProjectileTraits", ("ItemTrait_Projectile",)),
            ("BossTributes", ("BossTribute",)),
            ("VehicleParts", ("Car_", "Ship", "Raft")),
            ("Recipes", ("RecipeNote", "CustomFoodRecipe", "CustomDrinkRecipe")),
            ("RepairKits", ("RepairKit",)),
            ("TreasureMaps", ("TreasureMap",)),
            ("Spawners", ("Spawner",)),
            ("DungeonEntrances", ("DungeonEntrance",)),
            ("Taxidermy", ("Taxidermy",)),
            ("Inventories", ("PrimalInventory",)),
            ("Buffs", ("Buff",)),
        ],
    ),
    dict(
        module="world",
        aggregate="World",
        header="World actors: loot drops, boss arenas, mission managers and vehicles.",
        categories=["drops", "world", "vehicles"],
        fallback="Misc",
        rules=[
            ("SupplyCrates", ("SupplyCrate", "ElementWall_Horde")),
            ("ArtifactCrates", ("ArtifactCrate",)),
            ("DroppedItems", ("DroppedItem",)),
            ("Nests", ("Nest",)),
            ("BossArenas", ("BossArenaManager",)),
            ("Missions", ("MissionManager", "MissionDispatcher", "NPCZoneManager")),
            ("DayCycles", ("DayCycle",)),
            ("Vehicles", ("Raft", "Car_Vehicle", "Zeppelin", "Ship")),
        ],
    ),
]

# Modules that already exist. ``existing`` names the classes a rule should
# append to instead of creating; everything else becomes a new sibling class
# that is registered on the module's roll-up class.
EXTENSIONS = [
    dict(
        module="resources",
        aggregate="Resources",
        categories=["resources"],
        fallback="Basic",
        existing=["Basic", "Crafted", "ApexDrop"],
        rules=[
            ("ApexDrop", ("ApexDrop", "RareDrop")),
            ("Crafted", ("Refined", "Ingot", "Dust", "Polymer", "Gasoline",
                         "Propellant", "Paste", "Powder", "Silicate")),
        ],
    ),
    dict(
        module="consumables",
        aggregate="Consumables",
        categories=["consumables"],
        fallback="Misc",
        # Every one of the 190 eggs says "Egg"; the class it lands in says it too.
        noise=("Egg",),
        existing=["Seeds", "Misc"],
        rules=[
            ("UnderwaterEggs", ("UnderwaterEgg",)),
            ("FertilizedEggs", ("Fertilized",)),
            ("Eggs", ("Egg",)),
            ("Emotes", ("UnlockEmote",)),
            ("Seeds", ("Seed",)),
            ("Veggies", ("Veggie",)),
            ("CakeSlices", ("CakeSlice",)),
            ("Embryos", ("Embryo",)),
        ],
    ),
    dict(
        module="dinos",
        aggregate="Dinos",
        categories=["dinos"],
        fallback="Misc",
        noise=DINO_NOISE,
        keep_markers=True,
        existing=["Abberant", "Corrupted", "Alphas", "event"],
        rules=[
            ("Thralls", ("Thrall",)),
            ("Corrupted", ("Zombie", "Corrupt")),
            ("Lightning", ("Lightning",)),
            ("Abberant", ("Aberrant",)),
            ("Alphas", ("ALPHA_", "Mega")),
            ("Astral", ("Astral",)),
            ("BiomeVariants", ("Bog_", "Ocean_", "Snow_", "Volcano_", "Lunar_")),
            ("event", ("Bunny",)),
        ],
    ),
    dict(
        module="placed_structures",
        aggregate="PlacedStructures",
        categories=["structures"],
        fallback="Misc",
        noise=STRUCTURE_NOISE,
        existing=["Stone", "Metal", "Thatch", "Adobe", "Tek", "Wood", "Crafting",
                  "Utility", "TributeTerminals", "Water", "Turrets", "Aberration"],
        rules=MATERIALS + STRUCTURE_ROLES,
    ),
    dict(
        module="equipment",
        aggregate="Equipment",
        categories=["armor", "saddles", "weapons", "ammo"],
        fallback="Tools",
        existing=["Saddles", "Ammo", "Shields", "Utilities", "Tools"],
        rules=[
            ("Attachments", ("WeaponAttachment",)),
            ("Saddles", ("Saddle", "Platform", "ForSBear", "MekBackpack", "MekTransformer")),
            ("Ammo", ("Ammo",)),
            ("Shields", ("Shield",)),
            ("Utilities", ("Glider", "Zipline")),
        ],
    ),
]
