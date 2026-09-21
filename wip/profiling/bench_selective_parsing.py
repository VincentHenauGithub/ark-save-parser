"""Benchmark for selective / exclusion-filtered object parsing.

Each scenario builds a fresh AsaSave so nothing is shared between runs. Run one
scenario per process for clean numbers.

usage: python bench_selective_parsing.py <scenario> <save_path> [reps]

scenarios:
  load                  save open only (control)
  objects_all           get_game_objects, every property decoded
  objects_sel           get_game_objects, only the properties DinoApi reads
  objects_min           get_game_objects, a 3-property selection
  objects_none          selection matching nothing: the floor, i.e. all the cost
                        that is NOT property decoding (SQLite + names + objects)
  objects_excl          get_game_objects with excluded_property_names
  objects_excl_baseline the same result the slow way: parse all, then filter
  dino_all              DinoApi.get_all()
  dino_sel              DinoApi.get_all() with a selection

Measured on tests/test_data/set_2/Ragnarok_WP/Ragnarok_WP.ark (4612 matched
objects, 112k properties), best of 9, Python 3.13:

  objects_all             0.662s   (baseline 0.668s - unchanged)
  objects_sel             0.595s   -11%
  objects_min             0.524s   -21%
  objects_none            0.485s   -27%  <- ceiling of selective parsing
  objects_excl            0.469s   -29%  vs objects_excl_baseline 0.659s
  dino_all                0.767s   (baseline 0.753s - unchanged)
  dino_sel                0.664s   -12%

Property decoding is only ~27% of this workload; the rest is SQLite, the name
table and object construction. Selection cannot beat that ceiling. Exclusion
can, because it drops whole objects before any of that work happens.
"""
import gc
import json
import sys
import time
from pathlib import Path

SCENARIO, SAVE_PATH = sys.argv[1], sys.argv[2]
REPS = int(sys.argv[3]) if len(sys.argv) > 3 else 5

from arkparse import AsaSave                                   # noqa: E402
from arkparse.api.dino_api import DinoApi                      # noqa: E402
from arkparse.parsing import GameObjectReaderConfiguration     # noqa: E402
from arkparse.logging import ArkSaveLogger                     # noqa: E402

ArkSaveLogger.allow_invalid_objects(True)

# The properties Dino/TamedDino/Baby/DinoStats actually read in __init_props__.
DINO_PROPS = [
    # Dino
    "bIsFemale", "DinoID1", "DinoID2", "GeneTraits", "bIsDead",
    "SavedBaseWorldLocation", "MyCharacterStatusComponent", "Owner",
    # TamedDino / Baby
    "TamedName", "TamerString", "TamingTeamID", "TargetingTeam", "TamedTimeStamp",
    "OwningPlayerID", "OwningPlayerName", "MyInventoryComponent", "bIsBaby", "BabyAge",
    # DinoStats
    "BaseCharacterLevel", "DinoImprintingQuality",
    "NumberOfLevelUpPointsApplied", "NumberOfLevelUpPointsAppliedTamed",
    "NumberOfMutationsAppliedTamed", "CurrentStatusValues",
]

# Properties that are big and that a "wild dino stats" pass never looks at.
# "CurrentStatusValues" is carried by every DinoCharacterStatusComponent in this
# save (2304 of the 4612 matched objects), so excluding it is a real, measurable
# halving of the object set rather than a no-op.
EXCLUDE_PROPS = ["CurrentStatusValues"]

# Near-minimal selection: the ceiling of what skipping can buy.
MIN_PROPS = ["BaseCharacterLevel", "SavedBaseWorldLocation", "MyCharacterStatusComponent"]


def make_cfg(selected=None, excluded=None):
    base = DinoApi._DEFAULT_CONFIG
    kwargs = dict(blueprint_name_filter=base.blueprint_name_filter)
    if selected is not None:
        kwargs["selected_property_names"] = list(selected)
    if excluded is not None:
        kwargs["excluded_property_names"] = list(excluded)
    return GameObjectReaderConfiguration(**kwargs)


def scen_load():
    s = AsaSave(Path(SAVE_PATH))
    n = 0
    s.close()
    return n


def scen_objects_all():
    s = AsaSave(Path(SAVE_PATH))
    objs = s.get_game_objects(make_cfg())
    n = len(objs)
    s.close()
    return n


def scen_objects_sel():
    s = AsaSave(Path(SAVE_PATH))
    objs = s.get_game_objects(make_cfg(selected=DINO_PROPS))
    n = len(objs)
    s.close()
    return n


def scen_objects_excl():
    s = AsaSave(Path(SAVE_PATH))
    objs = s.get_game_objects(make_cfg(excluded=EXCLUDE_PROPS))
    n = len(objs)
    s.close()
    return n


def scen_dino_all():
    s = AsaSave(Path(SAVE_PATH))
    d = DinoApi(s).get_all()
    n = len(d)
    s.close()
    return n


def scen_dino_sel():
    s = AsaSave(Path(SAVE_PATH))
    d = DinoApi(s).get_all(config=make_cfg(selected=DINO_PROPS))
    n = len(d)
    s.close()
    return n


def scen_objects_min():
    s = AsaSave(Path(SAVE_PATH))
    objs = s.get_game_objects(make_cfg(selected=MIN_PROPS))
    n = len(objs)
    s.close()
    return n


def scen_objects_none():
    # Selection that matches nothing at all: the hard floor (SQLite + name table +
    # object construction with zero property decoding).
    s = AsaSave(Path(SAVE_PATH))
    objs = s.get_game_objects(make_cfg(selected=["__nothing_matches_this__"]))
    n = len(objs)
    s.close()
    return n


def scen_objects_excl_baseline():
    # What a caller must do without excluded_property_names: parse everything, then
    # drop the objects carrying the unwanted property.
    s = AsaSave(Path(SAVE_PATH))
    objs = s.get_game_objects(make_cfg())
    n = len({k: v for k, v in objs.items() if not any(v.has_property(p) for p in EXCLUDE_PROPS)})
    s.close()
    return n


SCENARIOS = {
    "objects_min": scen_objects_min,
    "objects_none": scen_objects_none,
    "objects_excl_baseline": scen_objects_excl_baseline,
    "load": scen_load,
    "objects_all": scen_objects_all,
    "objects_sel": scen_objects_sel,
    "objects_excl": scen_objects_excl,
    "dino_all": scen_dino_all,
    "dino_sel": scen_dino_sel,
}

fn = SCENARIOS[SCENARIO]
times = []
count = None
try:
    for _ in range(REPS):
        gc.collect()
        t0 = time.perf_counter()
        count = fn()
        times.append(time.perf_counter() - t0)
    out = {"scenario": SCENARIO, "ok": True,
           "times": times, "best": min(times), "median": sorted(times)[len(times) // 2],
           "count": count}
except Exception as exc:  # noqa: BLE001
    out = {"scenario": SCENARIO, "ok": False,
           "error": f"{type(exc).__name__}: {exc}"}

print("BENCHJSON " + json.dumps(out))
