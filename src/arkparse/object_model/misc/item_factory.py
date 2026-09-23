import os
from typing import Optional
from uuid import UUID

from arkparse.enums.ark_item_archetype import ArkItemArchetype
from arkparse.logging import ArkSaveLogger
from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase
from arkparse.object_model.misc.inventory_item import InventoryItem

# Archetype -> the template that carries its maximal property layout.
_TEMPLATES = {
    ArkItemArchetype.STACKABLE: ("stackable", "stackable"),
    ArkItemArchetype.TRAIT: ("trait", "trait"),
    ArkItemArchetype.STACKABLE_SPOILING: ("item", "stackable_spoiling"),
    ArkItemArchetype.TOOL: ("item", "tool"),
    ArkItemArchetype.SIMPLE: ("item", "simple"),
    ArkItemArchetype.SKIN: ("item", "skin"),
    ArkItemArchetype.CRYOPOD: ("item", "cryopod"),
    ArkItemArchetype.FERTILIZED_EGG: ("item", "fertilized_egg"),
    ArkItemArchetype.CUSTOM_RECIPE: ("item", "custom_recipe"),
}

# Substrings that identify an archetype on their own, tried before the class
# lists so a fertilized egg is never mistaken for an ordinary consumable.
_BY_NAME = [
    (ArkItemArchetype.CRYOPOD, ("Cryopod",)),
    (ArkItemArchetype.FERTILIZED_EGG, ("Fertilized", "Embryo")),
    (ArkItemArchetype.CUSTOM_RECIPE, ("CustomFoodRecipe", "CustomDrinkRecipe")),
    (ArkItemArchetype.TRAIT, ("ItemTrait",)),
    (ArkItemArchetype.SKIN, ("PrimalItemSkin", "PrimalItemCostume", "PrimalItemStructureSkin")),
    (ArkItemArchetype.SIMPLE, ("PrimalItemTrophy", "PrimalItemArtifact", "PrimalItemDye")),
    (ArkItemArchetype.STACKABLE, ("PrimalItemAmmo",)),
]


def _short_name(blueprint: str) -> str:
    return blueprint.rsplit("/", 1)[-1].split(".")[0]


def archetype_of(blueprint: str, is_blueprint: bool = False) -> ArkItemArchetype:
    """Which template a blueprint class has to be generated from.

    Takes any class value from ``arkparse.classes`` -- ``Classes.dyes.red.gore``,
    ``Classes.equipment.weapons.advanced.longneck`` -- or a raw blueprint path.
    ``is_blueprint`` selects the engram counterpart for equipment.
    """
    from arkparse.classes import Classes
    from arkparse.classes.equipment import Equipment as Eq

    name = _short_name(blueprint)

    for archetype, markers in _BY_NAME:
        if any(m in name for m in markers):
            return archetype

    # Equipment is classified the way EquipmentApi does it: by class list first,
    # falling back to the folder the asset sits in.
    for archetype, bps, folders in (
        (ArkItemArchetype.SADDLE, Eq.saddles.all_bps, ("/Saddles/", "/CursedSaddles/")),
        (ArkItemArchetype.SHIELD, Eq.shield.all_bps, ("/Armor/Shields/",)),
        (ArkItemArchetype.ARMOR, Eq.armor.all_bps, ("/Armor/", "/CursedArmor/")),
        (ArkItemArchetype.WEAPON, Eq.weapons.all_bps, ("/Weapons/", "/CursedWeapons/")),
    ):
        if blueprint in bps or any(f in blueprint for f in folders):
            return ArkItemArchetype(archetype.value + "_bp") if is_blueprint else archetype

    if blueprint in Classes.consumables.all_bps or "PrimalItemConsumable" in name:
        return ArkItemArchetype.STACKABLE_SPOILING
    if blueprint in Classes.resources.all_bps or "PrimalItemResource" in name:
        return ArkItemArchetype.STACKABLE
    if blueprint in Classes.trophies.all_bps:
        return ArkItemArchetype.SIMPLE
    if "PrimalItem_Weapon" in name or "PrimalItemStructure" in name:
        return ArkItemArchetype.TOOL

    ArkSaveLogger.warning_log(f"No archetype known for {name}, generating it as a plain item")
    return ArkItemArchetype.SIMPLE


def generate(save, blueprint: str, owner_inventory_uuid: Optional[UUID] = None,
             archetype: Optional[ArkItemArchetype] = None,
             is_blueprint: bool = False) -> InventoryItem:
    """Create an item of ``blueprint`` in ``save`` and return it.

    The archetype is worked out from the class unless one is passed explicitly.
    When ``owner_inventory_uuid`` is given the item is pointed at that inventory;
    adding it to the inventory's own item list is ``Inventory.add_item``.
    """
    archetype = archetype or archetype_of(blueprint, is_blueprint)

    if archetype.is_equipment:
        return _generate_equipment(save, blueprint, archetype, owner_inventory_uuid)

    folder, template = _TEMPLATES[archetype]
    uuid, _ = ParsedObjectBase._generate(save, os.path.join("templates", folder, template))
    item = InventoryItem(uuid, save)

    if save.save_context.get_name_id(blueprint) is None:
        save.add_name_to_name_table(blueprint)
    if owner_inventory_uuid is not None:
        item.replace_uuid(owner_inventory_uuid, item.owner_inv_uuid)
    item.reidentify(uuid, blueprint)

    # The template was taken from a real save, so its decay clock is stale.
    decay = item.object.find_property("LastAutoDurabilityDecreaseTime")
    if decay is not None:
        item.binary.replace_double(decay, save.save_context.game_time)
        item.update_binary()

    return item


def _generate_equipment(save, blueprint, archetype, owner_inventory_uuid):
    # Imported from the package, and only when actually generating equipment:
    # the equipment modules reach back into this one.
    from arkparse.object_model.equipment import Armor, Saddle, Shield, Weapon

    own_class = {"weapon": Weapon, "armor": Armor,
                 "saddle": Saddle, "shield": Shield}[archetype.value.removesuffix("_bp")]
    item = own_class.generate_from_template(blueprint, save, archetype.is_blueprint)
    if owner_inventory_uuid is not None:
        item.replace_uuid(owner_inventory_uuid, item.owner_inv_uuid)
        item.update_binary()
    return item


class ItemFactory:
    """Generate any inventory item from its blueprint class.

    Mirrors the ``X.generate_from_template`` style used elsewhere in the object
    model, for callers who would rather not import the module functions::

        item = ItemFactory.generate(save, Classes.dyes.red.gore)
    """

    archetype_of = staticmethod(archetype_of)
    generate = staticmethod(generate)
