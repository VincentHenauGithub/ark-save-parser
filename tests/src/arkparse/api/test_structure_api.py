
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
        ArkMap.EXTINCTION: 62142,
        ArkMap.ASTRAEOS: 130372,
        ArkMap.SCORCHED_EARTH: 27146,
        ArkMap.THE_ISLAND: 113156,
        ArkMap.THE_CENTER: 138498,
        ArkMap.LOST_COLONY: 19951,
        ArkMap.VALGUERO: 20915,
        ArkMap.GENESIS: 5850,
    }
    return strct.get(map, 0)

def test_structure_retrieval(map_save):
    """
    Test to retrieve structure information from the current map save.
    """
    map, save = map_save
    print(f"\nRetrieving structure information for map: {map.name.title()}")
    api = StructureApi(save)
    structures = api.get_all()

    print(f"  Total structures: {len(structures)}")

    # Maps without an explicit expectation fall back to "greater than zero".
    assert len(structures) >= max(structures_per_map(map), 1), f"Expected at least {max(structures_per_map(map), 1)} structures, got {len(structures)}"
