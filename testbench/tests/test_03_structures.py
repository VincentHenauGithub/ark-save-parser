"""Structure API: parse all structures and snapshot the count."""
import pytest

from arkparse.api import StructureApi
from arkparse.parsing.game_object_reader_configuration import GameObjectReaderConfiguration
from arkparse.saves.asa_save import AsaSave

from snapshot import Snapshot


@pytest.fixture(scope="module")
def structure_api(save) -> StructureApi:
    return StructureApi(save)


def test_get_all(structure_api: StructureApi, snapshot: Snapshot):
    structures = structure_api.get_all()
    assert isinstance(structures, dict), "Expected a dict of structures"
    print(f"Total structures: {len(structures)}")
    snapshot.check("structures_total", len(structures))


def test_with_inventory(structure_api: StructureApi, snapshot: Snapshot):
    with_inv = structure_api.get_all_with_inventory()
    print(f"Structures with inventory: {len(with_inv)}")
    snapshot.check("structures_with_inventory", len(with_inv))


def test_all_structures_with_id_are_parsed(structure_api: StructureApi, save):
    """Every game object carrying a StructureID property must show up in the
    parsed structure set."""
    structures = structure_api.get_all()

    print("fetching objects with StructureID properties")
    config = GameObjectReaderConfiguration()
    config.property_names = ["StructureID"]
    save: AsaSave = save
    with_id = save.get_game_objects(config)
    print(f"Found {len(with_id)} structures with StructureID property")

    parsed_ids = {uuid.bytes for uuid in structures.keys()}
    unparsed: dict[str, int] = {}
    for uuid2, obj in with_id.items():
        if uuid2.bytes not in parsed_ids:
            if obj.blueprint not in unparsed:
                print(f"Structure not found in parsed structures: {obj.blueprint} ({uuid2})")
            unparsed[obj.blueprint] = unparsed.get(obj.blueprint, 0) + 1

    count = sum(unparsed.values())
    if unparsed:
        print(f"{count} unparsed object(s) with StructureID, by blueprint:")
        for bp, n in sorted(unparsed.items(), key=lambda kv: kv[1], reverse=True):
            print(f"  {n:>6}  {bp}")

    assert count == 0, f"{count} structures with StructureID property not found in parsed structures"
