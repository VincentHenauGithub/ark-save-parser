
import json
import pytest
from pathlib import Path
from typing import Dict

from arkparse import AsaSave
from arkparse.api import StructureApi
from arkparse.enums import ArkMap
from arkparse.parsing.game_object_reader_configuration import GameObjectReaderConfiguration

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

def test_all_structures_with_id_are_parsed(map_save):
    """
    For each map, check that every game object carrying a StructureID property is
    represented in the parsed structure set.
    """
    map, save = map_save
    api = StructureApi(save)
    structures = api.get_all()

    print(f"[{map.name}] fetching objects with StructureID properties")
    config = GameObjectReaderConfiguration()
    config.property_names = ["StructureID"]
    with_id = save.get_game_objects(config)
    print(f"[{map.name}] Found {len(with_id)} objects with StructureID property")

    parsed_ids = {uuid.bytes for uuid in structures.keys()}
    count = 0
    unparsed_bps = set()
    for uuid2, obj in with_id.items():
        if uuid2.bytes not in parsed_ids:
            count += 1
            unparsed_bps.add(obj.blueprint)
            print(f"[{map.name}] Object with StructureID not in parsed structures: {obj.blueprint} ({uuid2}) count={count}")

    # Compile the detected (unparsed) blueprints into a single alphabetical,
    # unique list next to this test file (merged across all maps)
    _dump_path = Path(__file__).parent / "unparsed_structures_with_id.json"
    _existing = set(json.loads(_dump_path.read_text())) if _dump_path.exists() else set()
    _existing |= unparsed_bps
    _dump_path.write_text(json.dumps(sorted(_existing), indent=4))

    assert count == 0, f"[{map.name}] {count} objects with StructureID property not found in parsed structures"
