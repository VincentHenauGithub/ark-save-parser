"""
Compare the two ways of selecting structure/dino objects out of a save:

  "name"  the current approach: a `blueprint_name_filter` lambda that matches on
          substrings of the class path (what StructureApi/DinoApi use today).
  "id"    a `property_names` filter on the identity property the object type is
          supposed to carry ("StructureID" / "DinoID1"), which is a raw byte-
          pattern scan over each object's blob before it is parsed.

For each approach it reports wall time and object count, and then the set
difference between the two, so the trade-off (speed vs. what each one misses) is
visible for the save at hand.

Every measurement runs against a freshly opened AsaSave: SaveConnection caches
parsed objects, so reusing one save would make whichever approach runs second
look artificially fast.

Usage:
    python wip/profiling/compare_id_vs_name_filter.py [path/to/Map_WP.ark] [--json out.json]

With no path, the first .ark under testbench/test_save/ is used, falling back to
tests/test_data/set_1/Ragnarok_WP/Ragnarok_WP.ark.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Callable, Dict, List, Tuple
from uuid import UUID

from arkparse import AsaSave
from arkparse.api.dino_api import DinoApi
from arkparse.api.structure_api import StructureApi
from arkparse.logging import ArkSaveLogger
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import GameObjectReaderConfiguration

REPO_ROOT = Path(__file__).resolve().parents[2]


def _default_save() -> Path:
    testbench = REPO_ROOT / "testbench" / "test_save"
    if testbench.exists():
        found = sorted(testbench.rglob("*.ark"))
        if found:
            return found[0]
    return REPO_ROOT / "tests" / "test_data" / "set_1" / "Ragnarok_WP" / "Ragnarok_WP.ark"


def _name_config_structures() -> GameObjectReaderConfiguration:
    """The filter StructureApi.get_all_objects() builds today."""
    from arkparse.api._deviating_structures import (
        _KNOWN_DEVIATING_STRUCTURE_BPS,
        _KNOWN_NONE_STRUCTURES,
    )

    return GameObjectReaderConfiguration(
        blueprint_name_filter=lambda name: name is not None and (
            (name in _KNOWN_DEVIATING_STRUCTURE_BPS)
            or (
                ("Structures" in name)
                and (not "PrimalItemStructure_" in name or "PrimalItemStructure_ASR" in name)
                and (not "/Skins/" in name)
                and (not "PrimalInventory" in name)
                and (not "/TreasureMap/" in name)
                and (not "PrimalItemStructureSkin" in name)
                and (not "PrimalItemResource" in name)
                and (not "/TrainCarts/" in name)
                and (not name in _KNOWN_NONE_STRUCTURES)
            )
        )
    )


def _measure(save_path: Path, config: GameObjectReaderConfiguration) -> Tuple[float, Dict[UUID, ArkGameObject]]:
    """Open the save fresh, run one filtered retrieval, return (seconds, objects)."""
    save = AsaSave(save_path)
    try:
        start = time.perf_counter()
        objects = save.get_game_objects(config)
        elapsed = time.perf_counter() - start
        # Detach from the save so the objects survive close() for the diffing below.
        return elapsed, dict(objects)
    finally:
        save.close()


def _summarize_bps(objects: Dict[UUID, ArkGameObject], keys) -> List[Tuple[str, int]]:
    counts: Dict[str, int] = {}
    for key in keys:
        bp = objects[key].blueprint
        counts[bp] = counts.get(bp, 0) + 1
    return sorted(counts.items(), key=lambda kv: kv[1], reverse=True)


def _print_bps(title: str, bps: List[Tuple[str, int]], limit: int = 15) -> None:
    if not bps:
        return
    print(f"    {title} ({len(bps)} blueprint(s)):")
    for bp, n in bps[:limit]:
        print(f"      {n:>6}  {bp}")
    if len(bps) > limit:
        print(f"      ... and {len(bps) - limit} more blueprint(s)")


def compare(label: str, save_path: Path, name_config: GameObjectReaderConfiguration, id_property: str) -> dict:
    print(f"\n{'=' * 78}\n{label}\n{'=' * 78}")

    name_time, by_name = _measure(save_path, name_config)
    print(f"  name filter    : {len(by_name):>7} objects in {name_time:7.2f}s")

    id_config = GameObjectReaderConfiguration(property_names=[id_property])
    id_time, by_id = _measure(save_path, id_config)
    print(f"  {id_property:<14} : {len(by_id):>7} objects in {id_time:7.2f}s")

    if id_time > 0:
        ratio = name_time / id_time
        faster = "name filter" if ratio < 1 else f"{id_property} filter"
        print(f"  -> {faster} is {max(ratio, 1 / ratio):.2f}x faster")

    name_keys = set(by_name.keys())
    id_keys = set(by_id.keys())
    only_name = name_keys - id_keys
    only_id = id_keys - name_keys

    print(f"\n  shared         : {len(name_keys & id_keys)}")
    print(f"  only name      : {len(only_name)}  (would be LOST by switching to {id_property})")
    print(f"  only {id_property:<9} : {len(only_id)}  (would be GAINED by switching)")

    only_name_bps = _summarize_bps(by_name, only_name)
    only_id_bps = _summarize_bps(by_id, only_id)
    _print_bps(f"lost if switching to {id_property}", only_name_bps)
    _print_bps(f"gained by switching to {id_property}", only_id_bps)

    return {
        "label": label,
        "id_property": id_property,
        "name_filter": {"count": len(by_name), "seconds": round(name_time, 3)},
        "id_filter": {"count": len(by_id), "seconds": round(id_time, 3)},
        "shared": len(name_keys & id_keys),
        "only_name": len(only_name),
        "only_id": len(only_id),
        "only_name_blueprints": dict(only_name_bps),
        "only_id_blueprints": dict(only_id_bps),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("save", nargs="?", type=Path, default=None, help="path to a .ark save")
    parser.add_argument("--json", type=Path, default=None, help="write the results to this JSON file")
    parser.add_argument("--only", choices=["structures", "dinos"], default=None, help="run just one comparison")
    args = parser.parse_args()

    save_path = args.save or _default_save()
    if not save_path.exists():
        raise SystemExit(f"Save not found: {save_path}")

    ArkSaveLogger.disable_all_logs()
    ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.ERROR, True)
    ArkSaveLogger.allow_invalid_objects(True)
    ArkSaveLogger.allow_invalid_mod_objects(True)

    print(f"Save: {save_path}")

    results = []
    if args.only != "dinos":
        results.append(compare("STRUCTURES", save_path, _name_config_structures(), "StructureID"))
    if args.only != "structures":
        results.append(compare("DINOS", save_path, DinoApi._DEFAULT_CONFIG, "DinoID1"))

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps({"save": str(save_path), "results": results}, indent=4))
        print(f"\nWrote results to {args.json}")


if __name__ == "__main__":
    main()
