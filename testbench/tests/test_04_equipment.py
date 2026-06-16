"""Equipment API: parse armor / weapons / saddles / shields and snapshot counts."""
import pytest

from arkparse.api import EquipmentApi

from snapshot import Snapshot


@pytest.fixture(scope="module")
def eq_api(save) -> EquipmentApi:
    return EquipmentApi(save)


def test_armor(eq_api: EquipmentApi, snapshot: Snapshot):
    armor = eq_api.get_armor()
    print(f"Armor: {len(armor)}")
    snapshot.check("equipment_armor", len(armor))


def test_weapons(eq_api: EquipmentApi, snapshot: Snapshot):
    weapons = eq_api.get_weapons()
    print(f"Weapons: {len(weapons)}")
    snapshot.check("equipment_weapons", len(weapons))


def test_saddles(eq_api: EquipmentApi, snapshot: Snapshot):
    saddles = eq_api.get_saddles()
    print(f"Saddles: {len(saddles)}")
    snapshot.check("equipment_saddles", len(saddles))


def test_shields(eq_api: EquipmentApi, snapshot: Snapshot):
    shields = eq_api.get_shields()
    print(f"Shields: {len(shields)}")
    snapshot.check("equipment_shields", len(shields))
