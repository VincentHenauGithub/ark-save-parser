import pytest
import random
from uuid import uuid4
from pathlib import Path
from arkparse.api import EquipmentApi
from arkparse.classes.equipment import Equipment
from arkparse import AsaSave
from arkparse.enums import ArkMap, ArkEquipmentStat
from arkparse.logging import ArkSaveLogger
from arkparse.object_model.equipment import Armor, Saddle, Weapon, Shield

def diff(v1, v2, delta_percentage):
    delta = abs(v1 * delta_percentage)
    return abs(v1 - v2) <= delta

def equipment_per_map():
    """ Fixture to provide the expected number of equipment for each map. """
    return {
        ArkMap.RAGNAROK: {
            "armor": 1906,
            "weapons": 1517,
            "saddles": 2161,
            "shields": 87
        },
        ArkMap.ABERRATION: {
            "armor": 1024,
            "weapons": 394,
            "saddles": 481,
            "shields": 27
        },
        ArkMap.EXTINCTION: {
            "armor": 4279,
            "weapons": 2649,
            "saddles": 3110,
            "shields": 80
        },
        ArkMap.ASTRAEOS: {
            "armor": 6120,
            "weapons": 3757,
            "saddles": 8100,
            "shields": 205
        },
        ArkMap.SCORCHED_EARTH: {
            "armor": 1594,
            "weapons": 818,
            "saddles": 1565,
            "shields": 33
        },
        ArkMap.THE_ISLAND: {
            "armor": 6143,
            "weapons": 3857,
            "saddles": 6555,
            "shields": 216
        },
        ArkMap.THE_CENTER: {
            "armor": 6480,
            "weapons": 3818,
            "saddles": 7418,
            "shields": 208
        }
    }

@pytest.fixture(scope="module")
def eq_api(ragnarok_save):
    """
    Fixture to provide a EquipmentApi instance for the Ragnarok save.
    """
    resource = EquipmentApi(ragnarok_save)
    yield resource

def get_for_map(map_name: ArkMap, api: EquipmentApi):
    print(f"Testing equipment for map: {map_name}")

    armor = api.get_armor()
    print(f"Total Armor Items: {len(armor)}")
    assert len(armor) == equipment_per_map()[map_name]["armor"], "Unexpected number of armor items found"

    weapons = api.get_weapons()
    print(f"Total Weapon Items: {len(weapons)}")
    assert len(weapons) == equipment_per_map()[map_name]["weapons"], "Unexpected number of weapon items found."

    saddles = api.get_saddles()
    print(f"Total Saddle Items: {len(saddles)}")
    assert len(saddles) == equipment_per_map()[map_name]["saddles"], "Unexpected number of saddle items found."

    shields = api.get_shields()
    print(f"Total Shield Items: {len(shields)}")
    assert len(shields) == equipment_per_map()[map_name]["shields"], "Unexpected number of shield items found."

def test_parse_ragnarok(eq_api: EquipmentApi, enabled_maps: list):
    """
    Test to parse the Ragnarok save file and check the number of dinos.
    """
    if not ArkMap.RAGNAROK in enabled_maps:
        pytest.skip("Ragnarok map is not enabled in the test configuration.")

    get_for_map(ArkMap.RAGNAROK, eq_api)

def test_parse_aberration(aberration_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Aberration save file and check the number of dinos.
    """
    if not ArkMap.ABERRATION in enabled_maps:
        pytest.skip("Aberration map is not enabled in the test configuration.")
    eq_api = EquipmentApi(aberration_save)
    
    get_for_map(ArkMap.ABERRATION, eq_api)

def test_parse_extinction(extinction_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Extinction save file and check the number of dinos.
    """
    if not ArkMap.EXTINCTION in enabled_maps:
        pytest.skip("Extinction map is not enabled in the test configuration.")
    eq_api = EquipmentApi(extinction_save)

    get_for_map(ArkMap.EXTINCTION, eq_api)

def test_parse_astraeos(astraeos_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Astraeos save file and check the number of dinos.
    """
    if not ArkMap.ASTRAEOS in enabled_maps:
        pytest.skip("Astraeos map is not enabled in the test configuration.")
    eq_api = EquipmentApi(astraeos_save)

    get_for_map(ArkMap.ASTRAEOS, eq_api)

def test_parse_scorched_earth(scorched_earth_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Scorched Earth save file and check the number of dinos.
    """
    if not ArkMap.SCORCHED_EARTH in enabled_maps:
        pytest.skip("Scorched Earth map is not enabled in the test configuration.")
    eq_api = EquipmentApi(scorched_earth_save)

    get_for_map(ArkMap.SCORCHED_EARTH, eq_api)

def test_parse_the_island(the_island_save: AsaSave, enabled_maps: list):
    """
    Test to parse The Island save file and check the number of dinos.
    """
    if not ArkMap.THE_ISLAND in enabled_maps:
        pytest.skip("The Island map is not enabled in the test configuration.")
    eq_api = EquipmentApi(the_island_save)

    get_for_map(ArkMap.THE_ISLAND, eq_api)

def test_parse_the_center(the_center_save: AsaSave, enabled_maps: list):
    """
    Test to parse The Center save file and check the number of dinos.
    """
    if not ArkMap.THE_CENTER in enabled_maps:
        pytest.skip("The Center map is not enabled in the test configuration.")
    eq_api = EquipmentApi(the_center_save)
    get_for_map(ArkMap.THE_CENTER, eq_api)

def test_armor_generation_boundaries(eq_api: EquipmentApi):
    """
    Test the generation of armor items across different quality boundaries.
    """
    
    quality_boundaries = [0, 60]
    nr_of_tries = 50

    for _ in range(nr_of_tries):
        blueprint = random.choice(Equipment.armor.all_bps)
        item: Armor = eq_api.generate_equipment(EquipmentApi.Classes.ARMOR, blueprint, ArkEquipmentStat.ARMOR, min_value=quality_boundaries[0], max_value=quality_boundaries[1], from_rating=True, bp_chance=0.15)
        default_armor = Armor.get_default_armor(blueprint)
        default_dura = Armor.get_default_dura(blueprint)

        print(f"Generated Armor (bp:{'Yes' if item.is_bp else ' No'}): Quality: {item.quality}, Dura: {item.durability:.2f} ({Armor.get_internal_value(item, ArkEquipmentStat.DURABILITY)}), Armor: {item.armor:.2f} ({Armor.get_internal_value(item, ArkEquipmentStat.ARMOR)}) ({item.get_short_name()})")
        assert item.quality >= quality_boundaries[0] and item.quality <= quality_boundaries[1], "Generated armor quality is out of bounds."
        assert item.durability >= default_dura, "Generated armor durability is below the default value."
        assert item.armor >= default_armor, "Generated armor value is below the default value."

        # reparse item to ensure it is valid
        new_uuid = uuid4()
        eq_api.save.add_obj_to_db(new_uuid, item.binary.byte_buffer)
        item.reidentify(new_uuid)
        new_armor = Armor(new_uuid, eq_api.save)

        print(f"Reidentified Armor (bp:{'Yes' if item.is_bp else ' No'}): Quality: {new_armor.quality:.2f}, Dura: {new_armor.durability:.2f} ({Armor.get_internal_value(new_armor, ArkEquipmentStat.DURABILITY)}), Armor: {new_armor.armor:.2f} ({Armor.get_internal_value(new_armor, ArkEquipmentStat.ARMOR)}) ({new_armor.get_short_name()})")
        assert diff(new_armor.quality, item.quality, 0.1), "Reidentified armor quality does not match."
        assert diff(new_armor.durability, item.durability, 0.1), "Reidentified armor durability does not match."
        assert diff(new_armor.armor, item.armor, 0.1), "Reidentified armor value does not match."

    
def test_weapon_generation_boundaries(eq_api: EquipmentApi):
    """
    Test the generation of weapon items across different quality boundaries.
    """
    
    quality_boundaries = [0, 60]
    nr_of_tries = 50

    for _ in range(nr_of_tries):
        blueprint = random.choice(Equipment.weapons.all_bps)
        item: Weapon = eq_api.generate_equipment(EquipmentApi.Classes.WEAPON, blueprint, ArkEquipmentStat.DAMAGE, min_value=quality_boundaries[0], max_value=quality_boundaries[1], from_rating=True, bp_chance=0.15)
        default_damage = 100
        default_dura = Weapon.get_default_dura(blueprint)

        print(f"Generated Weapon (bp:{'Yes' if item.is_bp else ' No'}): Quality: {item.quality}, Dura: {item.durability:.2f} ({Weapon.get_internal_value(item, ArkEquipmentStat.DURABILITY)}), Damage: {item.damage:.2f} ({Weapon.get_internal_value(item, ArkEquipmentStat.DAMAGE)}) ({item.get_short_name()})")
        assert item.quality >= quality_boundaries[0] and item.quality <= quality_boundaries[1], "Generated weapon quality is out of bounds."
        assert item.durability >= default_dura, "Generated weapon durability is below the default value."
        assert item.damage >= default_damage, "Generated weapon damage is below the default value."

        # reparse item to ensure it is valid
        new_uuid = uuid4()
        eq_api.save.add_obj_to_db(new_uuid, item.binary.byte_buffer)
        item.reidentify(new_uuid)
        new_weapon = Weapon(new_uuid, eq_api.save)

        print(f"Reidentified Weapon (bp:{'Yes' if item.is_bp else ' No'}): Quality: {new_weapon.quality:.2f}, Dura: {new_weapon.durability:.2f} ({Weapon.get_internal_value(new_weapon, ArkEquipmentStat.DURABILITY)}), Damage: {new_weapon.damage:.2f} ({Weapon.get_internal_value(new_weapon, ArkEquipmentStat.DAMAGE)}) ({new_weapon.get_short_name()})")
        assert diff(new_weapon.quality, item.quality, 0.1), "Reidentified weapon quality does not match."
        assert diff(new_weapon.durability, item.durability, 0.1), "Reidentified weapon durability does not match."
        assert diff(new_weapon.damage, item.damage, 0.1), "Reidentified weapon damage does not match."


def test_saddle_generation_boundaries(eq_api: EquipmentApi):
    """
    Test the generation of saddle items across different quality boundaries.
    """
    
    quality_boundaries = [0, 60]
    nr_of_tries = 50

    for _ in range(nr_of_tries):
        blueprint = random.choice(Equipment.saddles.all_bps)
        item: Saddle = eq_api.generate_equipment(EquipmentApi.Classes.SADDLE, blueprint, ArkEquipmentStat.ARMOR, min_value=quality_boundaries[0], max_value=quality_boundaries[1], from_rating=True, bp_chance=0.15)
        default_armor = Saddle.get_default_armor(blueprint)
        default_dura = Saddle.get_default_dura(blueprint)

        print(f"Generated Saddle (bp:{'Yes' if item.is_bp else ' No'}): Quality: {item.quality}, Dura: {item.durability:.2f} ({Saddle.get_internal_value(item, ArkEquipmentStat.DURABILITY)}), Armor: {item.armor:.2f} ({Saddle.get_internal_value(item, ArkEquipmentStat.ARMOR)}) ({item.get_short_name()})")
        assert item.quality >= quality_boundaries[0] and item.quality <= quality_boundaries[1], "Generated saddle quality is out of bounds."
        assert item.durability >= default_dura, "Generated saddle durability is below the default value."
        assert item.armor >= default_armor, "Generated saddle armor is below the default value."

        # reparse item to ensure it is valid
        new_uuid = uuid4()
        eq_api.save.add_obj_to_db(new_uuid, item.binary.byte_buffer)
        item.reidentify(new_uuid)
        new_saddle = Saddle(new_uuid, eq_api.save)

        print(f"Reidentified Saddle (bp:{'Yes' if item.is_bp else ' No'}): Quality: {new_saddle.quality:.2f}, Dura: {new_saddle.durability:.2f} ({Saddle.get_internal_value(new_saddle, ArkEquipmentStat.DURABILITY)}), Armor: {new_saddle.armor:.2f} ({Saddle.get_internal_value(new_saddle, ArkEquipmentStat.ARMOR)}) ({new_saddle.get_short_name()})")
        assert diff(new_saddle.quality, item.quality, 0.1), "Reidentified saddle quality does not match."
        assert diff(new_saddle.durability, item.durability, 0.1), "Reidentified saddle durability does not match."
        assert diff(new_saddle.armor, item.armor, 0.1), "Reidentified saddle armor does not match."


def test_shield_generation_boundaries(eq_api: EquipmentApi):
    """
    Test the generation of shield items across different quality boundaries.
    """
    
    quality_boundaries = [0, 60]
    nr_of_tries = 50

    for _ in range(nr_of_tries):
        blueprint = random.choice(Equipment.shield.all_bps)
        item: Shield = eq_api.generate_equipment(EquipmentApi.Classes.SHIELD, blueprint, ArkEquipmentStat.DURABILITY, min_value=quality_boundaries[0], max_value=quality_boundaries[1], from_rating=True, bp_chance=0.15)
        default_dura = Shield.get_default_dura(blueprint)

        print(f"Generated Shield (bp:{'Yes' if item.is_bp else ' No'}): Quality: {item.quality}, Dura: {item.durability:.2f} ({Shield.get_internal_value(item, ArkEquipmentStat.DURABILITY)}) ({item.get_short_name()})")
        assert item.quality >= quality_boundaries[0] and item.quality <= quality_boundaries[1], "Generated shield quality is out of bounds."
        assert item.durability >= default_dura, "Generated shield durability is below the default value."

        # reparse item to ensure it is valid
        new_uuid = uuid4()
        eq_api.save.add_obj_to_db(new_uuid, item.binary.byte_buffer)
        item.reidentify(new_uuid)
        new_shield = Shield(new_uuid, eq_api.save)

        print(f"Reidentified Shield (bp:{'Yes' if item.is_bp else ' No'}): Quality: {new_shield.quality:.2f}, Dura: {new_shield.durability:.2f} ({Shield.get_internal_value(new_shield, ArkEquipmentStat.DURABILITY)}) ({new_shield.get_short_name()})")
        assert diff(new_shield.quality, item.quality, 0.1), "Reidentified shield quality does not match."
        assert diff(new_shield.durability, item.durability, 0.1), "Reidentified shield durability does not match."
