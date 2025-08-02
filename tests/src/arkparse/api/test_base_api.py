import pytest
from pathlib import Path
from arkparse.api import BaseApi
from arkparse.enums import ArkMap
from arkparse import AsaSave
from arkparse.classes import Classes
from arkparse.object_model.bases.base import Base
from arkparse.object_model.misc.object_owner import ObjectOwner
from arkparse.parsing.struct import ActorTransform, ArkVector
from arkparse.object_model.misc.inventory import Inventory

def count_files_in_folder(folder: Path) -> int:
    """
    Counts the number of files in a given folder.
    """
    if not folder.exists():
        return 0
    return sum(1 for _ in folder.iterdir() if _.is_file())

def get_file_names_in_folder(folder: Path) -> set:
    """
    Returns a set of file names in the given folder.
    """
    if not folder.exists():
        return set()
    all_files = {f.name for f in folder.iterdir() if f.is_file()}
    all_files.remove("base.json")  # Exclude base.json if it exists
    return all_files

def get_base_api(rag_limited: AsaSave, temp_file_folder: Path) -> BaseApi:
    rag_limited.store_db(temp_file_folder / "copy.db")
    assert (temp_file_folder / "copy.db").exists(), "Database file should be created"
    print(f"Database stored at {temp_file_folder / 'copy.db'}")
    save = AsaSave(path=temp_file_folder / "copy.db")
    assert save is not None, "AsaSave should be initialized"
    return BaseApi(save, ArkMap.RAGNAROK)

def test_base_api_initialization(rag_limited: AsaSave, resource_path: Path, temp_file_folder: Path):
    """
    Test the initialization of the BaseApi.
    """
    base_api = get_base_api(rag_limited, temp_file_folder)

    assert base_api is not None, "BaseApi should be initialized"
    assert isinstance(base_api, BaseApi), f"Expected BaseApi, got {type(base_api)}"
    assert base_api.save is not None, "BaseApi save should not be None"

def test_base_import(resource_path, temp_file_folder, rag_limited: AsaSave):
    """
    Test the import functionality of BaseApi.
    """
    base_api = get_base_api(rag_limited, temp_file_folder)

    base_path = resource_path / "bases" / "mixed_6"
    base = base_api.import_base(base_path)
    assert base is not None, "Imported base should not be None"
    print(f"Imported {count_files_in_folder(base_path)} files from base, base has {len(base.structures)} structures")

    base_api.save.store_db(temp_file_folder / "test_base_import.db")
    assert (temp_file_folder / "test_base_import.db").exists(), "Database file should be created"
    print(f"Database stored at {temp_file_folder / 'test_base_import.db'}")

    reimport_save = AsaSave(path = temp_file_folder / "test_base_import.db")
    reimport_api = BaseApi(reimport_save, ArkMap.RAGNAROK)
    reimport_base = reimport_api.get_base_at(base.location.as_map_coords(ArkMap.RAGNAROK), radius=1)
    assert reimport_base is not None, "Re-imported base should not be None"
    print(f"Re-imported base has {len(reimport_base.structures)} structures, nr of files: {count_files_in_folder(temp_file_folder / 'test_base_import')}")

    reimport_base.store_binary(temp_file_folder / "test_export")
    print(f"Exported {count_files_in_folder(temp_file_folder / 'test_export')} files to {temp_file_folder / 'test_export'}")

    assert count_files_in_folder(temp_file_folder / "test_export") > 0, "Exported files should exist"
    assert count_files_in_folder(temp_file_folder / "test_export") == count_files_in_folder(base_path), "Exported files count should match the original base files"

    file_names_original = get_file_names_in_folder(base_path)
    file_names_exported = get_file_names_in_folder(temp_file_folder / "test_export")

    for file_name in file_names_original:
        assert file_name not in file_names_exported, (
            f"File {file_name} from original base should not be in exported files"
        )

def test_base_import_at_location(resource_path, temp_file_folder, rag_limited: AsaSave):
    """
    Test the import functionality of BaseApi.
    """
    base_api = get_base_api(rag_limited, temp_file_folder)

    new_location = ActorTransform(vector=ArkVector(x=118368.11, y=172509.7, z=-10290))
    base_path = resource_path / "bases" / "mixed_6"
    base = base_api.import_base(base_path, new_location)
    assert base is not None, "Imported base should not be None"
    print(f"Imported {count_files_in_folder(base_path)} files from base, base has {len(base.structures)} structures")

    base_api.save.store_db(temp_file_folder / "test_base_import_at_location.db")
    assert (temp_file_folder / "test_base_import_at_location.db").exists(), "Database file should be created"
    print(f"Database stored at {temp_file_folder / 'test_base_import_at_location.db'}")

    reimport_save = AsaSave(path = temp_file_folder / "test_base_import_at_location.db")
    reimport_api = BaseApi(reimport_save, ArkMap.RAGNAROK)
    reimport_base = reimport_api.get_base_at(new_location.as_map_coords(ArkMap.RAGNAROK), radius=1)
    assert reimport_base is not None, "Re-imported base should not be None"
    print(f"Re-imported base has {len(reimport_base.structures)} structures, nr of files: {count_files_in_folder(temp_file_folder / 'test_base_import_at_location')}")

    reimport_base.store_binary(temp_file_folder / "test_export_at_location")
    print(f"Exported {count_files_in_folder(temp_file_folder / 'test_export_at_location')} files to {temp_file_folder / 'test_export_at_location'}")

    assert count_files_in_folder(temp_file_folder / "test_export_at_location") > 0, "Exported files should exist"
    assert count_files_in_folder(temp_file_folder / "test_export_at_location") == count_files_in_folder(base_path), "Exported files count should match the original base files"

def test_base_replace_owner(resource_path, temp_file_folder, rag_limited: AsaSave):
    """
    Test the replace owner functionality of BaseApi.
    """
    base_api = get_base_api(rag_limited, temp_file_folder)

    base_path = resource_path / "bases" / "mixed_6"
    base = base_api.import_base(base_path)
    assert base is not None, "Imported base should not be None"
    print(f"Imported {count_files_in_folder(base_path)} files from base, base has {len(base.structures)} structures")
    
    original_owner = base.owner
    o: ObjectOwner = ObjectOwner()
    o.set_tribe(171717, "Imaginarium")
    o.set_player(777, "The imagined")
    print(f"Replacing owner {original_owner} with {o}")

    base.set_owner(o)

    b = base_api.get_base_at(base.location.as_map_coords(ArkMap.RAGNAROK), radius=1)
    print(b.owner)

    base_api.save.store_db(temp_file_folder / "test_base_replace_owner.db")
    assert (temp_file_folder / "test_base_replace_owner.db").exists(), "Database file should be created"
    print(f"Database stored at {temp_file_folder / 'test_base_replace_owner.db'}")

    reimport_save = AsaSave(path=temp_file_folder / "test_base_replace_owner.db")
    reimport_api = BaseApi(reimport_save, ArkMap.RAGNAROK)
    reimport_base = reimport_api.get_base_at(base.location.as_map_coords(ArkMap.RAGNAROK), radius=1)
    assert reimport_base is not None, "Re-imported base should not be None"
    print(f"Re-imported base has {len(reimport_base.structures)} structures, owner: {reimport_base.owner}")
    assert reimport_base.owner == o, (f"Expected owner {o}, got {reimport_base.owner}")
    print(f"Re-imported base owner: {reimport_base.owner}")

    reimport_base.store_binary(temp_file_folder / "test_export_replace_owner")
    print(f"Exported {count_files_in_folder(temp_file_folder / 'test_export_replace_owner')} files to {temp_file_folder / 'test_export_replace_owner'}")
    
    nr_of_structures_old = len(base.structures)
    nr_of_structures_new = len(reimport_base.structures)
    files_old = count_files_in_folder(resource_path / "bases" / "mixed_6")
    files_new = count_files_in_folder(temp_file_folder / "test_export_replace_owner")

    assert files_new == files_old, (
        f"Expected {files_old} files, got {files_new}"
    )

    assert nr_of_structures_new == nr_of_structures_old, (
        f"Expected {nr_of_structures_old} structures, got {nr_of_structures_new}"
    )

def test_retrieving_nr_of_generators(rag_limited: AsaSave, temp_file_folder: Path, resource_path: Path):
    """
    Test retrieving the number of generators in a base.
    """
    base_api = get_base_api(rag_limited, temp_file_folder)
    base_path = resource_path / "bases" / "mixed_6"
    base = base_api.import_base(base_path)
    assert base is not None, "Imported base should not be None"

    elec_gens = base.get_generators(Base.GeneratorType.ELECTRIC)
    print(f"Found {len(elec_gens)} electric generators in the base")
    assert len(elec_gens) == 2, "Expected 2 electric generators in the base"

    tek_gens = base.get_generators(Base.GeneratorType.TEK)
    print(f"Found {len(tek_gens)} tek generators in the base")
    assert len(tek_gens) == 1, "Expected 1 tek generator in the base"

def test_retrieving_nr_of_turrets(rag_limited: AsaSave, temp_file_folder: Path, resource_path: Path):
    """
    Test retrieving the number of turrets in a base.
    """
    base_api = get_base_api(rag_limited, temp_file_folder)
    base_path = resource_path / "bases" / "mixed_6"
    base = base_api.import_base(base_path)
    assert base is not None, "Imported base should not be None"

    turrets = base.get_turrets(Base.TurretType.AUTO)
    print(f"Found {len(turrets)} auto turrets in the base")
    assert len(turrets) == 0, "Expected 0 auto turrets in the base"

    heavy_turrets = base.get_turrets(Base.TurretType.HEAVY)
    print(f"Found {len(heavy_turrets)} heavy turrets in the base")
    assert len(heavy_turrets) == 27, "Expected 27 heavy turrets in the base"

    tek_turrets = base.get_turrets(Base.TurretType.TEK)
    print(f"Found {len(tek_turrets)} tek turrets in the base")
    assert len(tek_turrets) == 12, "Expected 12 tek turrets in the base"

def count_stacks(inventory: Inventory, item_type: str) -> int:
    """
    Count the number of stacks of a specific item type in the inventory.
    """
    total = 0
    for item in inventory.items.values():
        if item.object.blueprint == item_type:
            print(f"Found item {item.get_short_name()} with quantity {item.quantity}")
            total += item.quantity
    return total

def test_generator_fuel(rag_limited: AsaSave, temp_file_folder: Path, resource_path: Path):
    """
    Test the fuel consumption of tek generators in a base.
    """
    base_api = get_base_api(rag_limited, temp_file_folder)
    base_path = resource_path / "bases" / "mixed_6"
    base = base_api.import_base(base_path)
    assert base is not None, "Imported base should not be None"

    base.set_fuel_in_generators(base_api.save, 37, 117)
    print(f"Set fuel in generators, now checking inventory")

    tek_gens = base.get_generators(Base.GeneratorType.TEK)
    for gen in tek_gens:
        nr_of_element = count_stacks(gen.inventory, Classes.resources.Basic.element)
        print(f"Generator {gen.object.uuid} has {nr_of_element} Element in inventory")
        assert nr_of_element == 37, f"Expected 37 Element in generator inventory, got {nr_of_element}"

    for elec_gen in base.get_generators(Base.GeneratorType.ELECTRIC):
        nr_of_fuel = count_stacks(elec_gen.inventory, Classes.resources.Crafted.gasoline)
        print(f"Generator {elec_gen.object.uuid} has {nr_of_fuel} Fuel in inventory")
        assert nr_of_fuel == 117, f"Expected 117 Fuel in electric generator inventory, got {nr_of_fuel}"

    base_api.save.store_db(temp_file_folder / "test_generator_fuel.db")
    assert (temp_file_folder / "test_generator_fuel.db").exists(), "Database file should be created"
    print(f"Database stored at {temp_file_folder / 'test_generator_fuel.db'}")

    reimport_save = AsaSave(path=temp_file_folder / "test_generator_fuel.db")
    reimport_api = BaseApi(reimport_save, ArkMap.RAGNAROK)
    reimport_base = reimport_api.get_base_at(base.location.as_map_coords(ArkMap.RAGNAROK), radius=1)
    assert reimport_base is not None, "Re-imported base should not be None"

    print(f"Re-imported base has {len(reimport_base.structures)} structures, nr of files: {count_files_in_folder(temp_file_folder / 'test_generator_fuel')}")

    tek_gens = base.get_generators(Base.GeneratorType.TEK)
    for gen in tek_gens:
        nr_of_element = count_stacks(gen.inventory, Classes.resources.Basic.element)
        print(f"Generator {gen.object.uuid} has {nr_of_element} Element in inventory")
        assert nr_of_element == 37, f"Expected 37 Element in generator inventory, got {nr_of_element}"

    for elec_gen in base.get_generators(Base.GeneratorType.ELECTRIC):
        nr_of_fuel = count_stacks(elec_gen.inventory, Classes.resources.Crafted.gasoline)
        print(f"Generator {elec_gen.object.uuid} has {nr_of_fuel} Fuel in inventory")
        assert nr_of_fuel == 117, f"Expected 117 Fuel in electric generator inventory, got {nr_of_fuel}"

def test_turret_ammo(rag_limited: AsaSave, temp_file_folder: Path, resource_path: Path):
    """
    Test the ammo consumption of turrets in a base.
    """
    base_api = get_base_api(rag_limited, temp_file_folder)
    base_path = resource_path / "bases" / "mixed_6"
    base = base_api.import_base(base_path)
    assert base is not None, "Imported base should not be None"

    # Test single stack
    base.set_turret_ammo(base_api.save, bullets_in_heavy=100, shards_in_tek=1000)
    print(f"Set ammo in turrets, now checking inventory")
    for heavy_turret in base.get_turrets(Base.TurretType.HEAVY):
        nr_of_ammo = count_stacks(heavy_turret.inventory, Classes.equipment.ammo.advanced_rifle_bullet)
        print(f"Heavy Turret {heavy_turret.object.uuid} has {nr_of_ammo} Advanced Rifle Bullets in inventory")
        assert nr_of_ammo == 100, f"Expected 100 Advanced Rifle Bullets in heavy turret inventory, got {nr_of_ammo}"

    for tek_turret in base.get_turrets(Base.TurretType.TEK):
        nr_of_ammo = count_stacks(tek_turret.inventory, Classes.resources.Basic.element_shard)
        print(f"Tek Turret {tek_turret.object.uuid} has {nr_of_ammo} Element Shards in inventory")
        assert nr_of_ammo == 1000, f"Expected 1000 Element Shards in tek turret inventory, got {nr_of_ammo}"

    base.set_turret_ammo(base_api.save, bullets_in_heavy=2345, shards_in_tek=1717)
    for heavy_turret in base.get_turrets(Base.TurretType.HEAVY):
        nr_of_ammo = count_stacks(heavy_turret.inventory, Classes.equipment.ammo.advanced_rifle_bullet)
        print(f"Heavy Turret {heavy_turret.object.uuid} has {nr_of_ammo} Advanced Rifle Bullets in inventory")
        assert nr_of_ammo == 2345, f"Expected 2345 Advanced Rifle Bullets in heavy turret inventory, got {nr_of_ammo}"

    for tek_turret in base.get_turrets(Base.TurretType.TEK):
        nr_of_ammo = count_stacks(tek_turret.inventory, Classes.resources.Basic.element_shard)
        print(f"Tek Turret {tek_turret.object.uuid} has {nr_of_ammo} Element Shards in inventory")
        assert nr_of_ammo == 1717, f"Expected 1717 Element Shards in tek turret inventory, got {nr_of_ammo}"

    base_api.save.store_db(temp_file_folder / "test_turret_ammo.db")
    assert (temp_file_folder / "test_turret_ammo.db").exists(), "Database file should be created"
    print(f"Database stored at {temp_file_folder / 'test_turret_ammo.db'}")

    reimport_save = AsaSave(path=temp_file_folder / "test_turret_ammo.db")
    reimport_api = BaseApi(reimport_save, ArkMap.RAGNAROK)
    reimport_base = reimport_api.get_base_at(base.location.as_map_coords(ArkMap.RAGNAROK), radius=1)
    assert reimport_base is not None, "Re-imported base should not be None"

    print(f"Re-imported base has {len(reimport_base.structures)} structures, nr of files: {count_files_in_folder(temp_file_folder / 'test_turret_ammo')}")
    for heavy_turret in reimport_base.get_turrets(Base.TurretType.HEAVY):
        nr_of_ammo = count_stacks(heavy_turret.inventory, Classes.equipment.ammo.advanced_rifle_bullet)
        print(f"Heavy Turret {heavy_turret.object.uuid} has {nr_of_ammo} Advanced Rifle Bullets in inventory")
        assert nr_of_ammo == 2345, f"Expected 2345 Advanced Rifle Bullets in heavy turret inventory, got {nr_of_ammo}"

    for tek_turret in reimport_base.get_turrets(Base.TurretType.TEK):
        nr_of_ammo = count_stacks(tek_turret.inventory, Classes.resources.Basic.element_shard)
        print(f"Tek Turret {tek_turret.object.uuid} has {nr_of_ammo} Element Shards in inventory")
        assert nr_of_ammo == 1717, f"Expected 1717 Element Shards in tek turret inventory, got {nr_of_ammo}"

    

