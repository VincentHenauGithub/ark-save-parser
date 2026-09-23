"""Item generation: one template per archetype, and growing an empty inventory.

Everything here writes to the save, so it runs against a copy rather than the
shared session fixture.
"""
import shutil
from pathlib import Path

import pytest

from arkparse.classes import Classes
from arkparse.enums import ArkItemArchetype
from arkparse.object_model.misc.inventory import Inventory
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.object_model.misc.item_factory import ItemFactory
from arkparse.saves.asa_save import AsaSave

STORAGE_BOX = ("/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_StorageBox."
               "PrimalInventoryBP_StorageBox_C")
CRYOPOD = ("/Game/Extinction/CoreBlueprints/Weapons/PrimalItem_WeaponEmptyCryopod."
           "PrimalItem_WeaponEmptyCryopod_C")


@pytest.fixture(scope="module")
def writable_save(save_file: Path, tmp_path_factory: pytest.TempPathFactory) -> AsaSave:
    """A throwaway copy of the save, safe to generate objects into."""
    target = tmp_path_factory.mktemp("generation") / save_file.name
    shutil.copy(save_file, target)
    return AsaSave(target)


# The archetype has to be decided from the class alone, since that is all a
# caller passes to ItemFactory.generate.
@pytest.mark.parametrize("blueprint, expected", [
    (Classes.dyes.red.gore, ArkItemArchetype.SIMPLE),
    (Classes.trophies.skeletons.all_bps[0], ArkItemArchetype.SIMPLE),
    (Classes.resources.Basic.metal, ArkItemArchetype.STACKABLE),
    (Classes.consumables.berries.mejoberry, ArkItemArchetype.STACKABLE_SPOILING),
    (Classes.consumables.fertilized_eggs.all_bps[0], ArkItemArchetype.FERTILIZED_EGG),
    (Classes.skins.chibis.all_bps[0], ArkItemArchetype.SKIN),
    (CRYOPOD, ArkItemArchetype.CRYOPOD),
    (Classes.equipment.weapons.advanced.longneck, ArkItemArchetype.WEAPON),
    (Classes.equipment.saddles.rex, ArkItemArchetype.SADDLE),
    (Classes.equipment.armor.flak.helmet, ArkItemArchetype.ARMOR),
])
def test_archetype_dispatch(blueprint: str, expected: ArkItemArchetype):
    assert ItemFactory.archetype_of(blueprint) is expected


def test_equipment_dispatch_has_blueprint_variant():
    """Engrams share a class with the item but need the _bp template."""
    item = ItemFactory.archetype_of(Classes.equipment.weapons.advanced.longneck)
    engram = ItemFactory.archetype_of(Classes.equipment.weapons.advanced.longneck,
                                      is_blueprint=True)
    assert not item.is_blueprint and engram.is_blueprint
    assert engram is ArkItemArchetype.WEAPON_BP


# Every generated item must come back out of the save as the class that was
# asked for -- not the class of the template it was stamped from.
@pytest.mark.parametrize("blueprint", [
    Classes.dyes.red.gore,
    Classes.resources.Basic.metal,
    Classes.consumables.berries.mejoberry,
    Classes.consumables.fertilized_eggs.all_bps[0],
    Classes.skins.chibis.all_bps[0],
    CRYOPOD,
    Classes.equipment.weapons.advanced.longneck,
    Classes.equipment.saddles.rex,
])
def test_generated_item_round_trips(writable_save: AsaSave, blueprint: str):
    item = ItemFactory.generate(writable_save, blueprint)

    reread = InventoryItem(item.object.uuid, writable_save)
    assert reread.object is not None, "generated item is not readable back from the save"
    assert reread.object.blueprint == blueprint


# A template is only useful if it carries the properties its archetype is
# defined by: they can be written later, but never added.
@pytest.mark.parametrize("blueprint, required", [
    (CRYOPOD, ["AssociatedDinoID1", "AssociatedDinoID2", "CustomItemDatas"]),
    (Classes.consumables.fertilized_eggs.all_bps[0],
     ["EggNumberOfLevelUpPointsApplied", "EggDinoAncestors", "EggColorSetIndices"]),
    (Classes.skins.chibis.all_bps[0], ["ItemColorID"]),
    (Classes.consumables.berries.mejoberry, ["ItemQuantity", "NextSpoilingTime"]),
    (Classes.equipment.weapons.advanced.longneck,
     ["SavedDurability", "ItemRating", "ItemQualityIndex", "ItemStatValues"]),
])
def test_template_carries_its_defining_properties(writable_save: AsaSave, blueprint: str,
                                                  required: list):
    item = ItemFactory.generate(writable_save, blueprint)
    present = {p.name for p in item.object.properties}
    missing = [name for name in required if name not in present]
    assert not missing, f"{blueprint} generated without {missing}"


def test_generated_inventory_is_empty_and_correctly_classed(writable_save: AsaSave):
    inventory = Inventory.generate_from_template(writable_save, STORAGE_BOX)
    assert inventory.object.blueprint == STORAGE_BOX
    assert inventory.number_of_items == 0


def test_items_can_be_added_to_an_empty_inventory(writable_save: AsaSave):
    """The first item has to insert the InventoryItems array; the rest replace it."""
    inventory = Inventory.generate_from_template(writable_save, STORAGE_BOX)
    assert inventory.number_of_items == 0

    added = []
    for _ in range(3):
        item = ItemFactory.generate(writable_save, Classes.resources.Basic.metal,
                                    owner_inventory_uuid=inventory.object.uuid)
        inventory.add_item(item.object.uuid)
        added.append(item.object.uuid)

    # Re-read from the save rather than trusting the in-memory object.
    reread = Inventory(inventory.object.uuid, writable_save)
    assert reread.number_of_items == 3
    assert set(reread.item_classes) == set(added)
    for item_class in reread.item_classes.values():
        assert item_class == Classes.resources.Basic.metal
