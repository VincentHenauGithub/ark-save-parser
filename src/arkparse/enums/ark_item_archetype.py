from enum import Enum


class ArkItemArchetype(Enum):
    """The template an item has to be generated from.

    ARK only serialises properties whose value differs from the class default,
    so what a saved item carries depends on its state, not only on its kind: the
    same crossbow shows up in dozens of property layouts. Generation cannot rely
    on that, because every write in this library replaces a property that is
    already present -- a property missing from the template can never be set.

    Each member therefore names a *maximal* layout: the richest shape an item of
    that kind was ever seen in, so anything the object model may want to write is
    already there. Two kinds need separate templates exactly when their maximal
    layouts differ.
    """

    # Gear: durability + stat values + rating + quality index.
    WEAPON = "weapon"
    ARMOR = "armor"
    SADDLE = "saddle"
    SHIELD = "shield"

    # The blueprint (engram) counterpart of each of the four above.
    WEAPON_BP = "weapon_bp"
    ARMOR_BP = "armor_bp"
    SADDLE_BP = "saddle_bp"
    SHIELD_BP = "shield_bp"

    # Counted items. STACKABLE has no spoil timers; STACKABLE_SPOILING does, and
    # is what food and other perishables need.
    STACKABLE = "stackable"
    STACKABLE_SPOILING = "stackable_spoiling"

    # Durability without any of the gear statistics: canteens, repair kits.
    TOOL = "tool"

    # No quantity, no durability, no statistics: trophies, artifacts, notes, dyes.
    SIMPLE = "simple"

    # Item traits, which carry their own small property set.
    TRAIT = "trait"

    # Cosmetics, which carry colour and custom-data properties.
    SKIN = "skin"

    # A cryopod: the only items carrying AssociatedDinoID1/2.
    CRYOPOD = "cryopod"

    # A fertilized egg or embryo: ancestry, mutations and per-stat level points.
    FERTILIZED_EGG = "fertilized_egg"

    # A player-authored food or drink recipe: custom name, description, colours.
    CUSTOM_RECIPE = "custom_recipe"

    @property
    def is_equipment(self) -> bool:
        """Does this archetype go through the Equipment model?"""
        return self in _EQUIPMENT

    @property
    def is_blueprint(self) -> bool:
        """Is this the engram counterpart rather than the item itself?"""
        return self.value.endswith("_bp")


_EQUIPMENT = frozenset({
    ArkItemArchetype.WEAPON, ArkItemArchetype.ARMOR,
    ArkItemArchetype.SADDLE, ArkItemArchetype.SHIELD,
    ArkItemArchetype.WEAPON_BP, ArkItemArchetype.ARMOR_BP,
    ArkItemArchetype.SADDLE_BP, ArkItemArchetype.SHIELD_BP,
})
