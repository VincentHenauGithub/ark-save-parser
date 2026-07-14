"""Structure API: parse all structures and snapshot the count."""
import pytest

from arkparse.api import StructureApi

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
