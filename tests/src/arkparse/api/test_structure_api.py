
import pytest
from typing import Dict

from arkparse import AsaSave
from arkparse.api import StructureApi
from arkparse.enums import ArkMap

def structures_per_map(map: ArkMap) -> int:
    """ Fixture to provide the expected number of dinos for each map. """
    strct = {
        ArkMap.RAGNAROK: 54838,
        ArkMap.ABERRATION: 22940,
        ArkMap.EXTINCTION: 62135,
        ArkMap.ASTRAEOS: 130372,
        ArkMap.SCORCHED_EARTH: 27143,
        ArkMap.THE_ISLAND: 113156,
        ArkMap.THE_CENTER: 138494
    }
    return strct.get(map, 0)

@pytest.fixture(scope="module")
def structure_apis(enabled_map_objects):
    """
    Fixture to provide a StructureApi instance for the enabled map saves.
    """
    resources = {map: StructureApi(save) for map, save in enabled_map_objects.items()}
    yield resources

def test_structure_retrieval(structure_apis: Dict[ArkMap, StructureApi], enabled_map_objects: Dict[ArkMap, AsaSave]):
    """
    Test to retrieve game time information from all enabled map saves.
    """
    print("\nRetrieving structure information from enabled map saves:")
    for map, _ in enabled_map_objects.items():
        print(f"Map: {map.name.title()}")
        api = structure_apis[map]
        structures = api.get_all()

        print(f"  Total structures: {len(structures)}")

        assert len(structures) >= structures_per_map(map), f"Expected {structures_per_map(map)} structures, got {len(structures)}"
