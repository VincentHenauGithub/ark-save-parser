"""Core parsing: the save loads, has no faulty objects, exposes game time,
and the general object API returns a stable object count.

Also covers the two things a single clean parse cannot show on its own:
that the parse is *reproducible* (see test_reparse_is_stable) and how many
names it had to invent to get through (see test_unresolved_names)."""
import gc
import os
import time

import pytest

from arkparse import AsaSave
from arkparse.api.general_api import GeneralApi
from arkparse.saves.save_connection import _PARALLEL_ENABLED

from snapshot import Snapshot
from debug import DEBUG_DIR


def test_save_loads(save: AsaSave, save_file):
    assert save is not None, "AsaSave failed to initialize"
    print(f"Loaded: {save_file} ({save_file.stat().st_size / 1e6:.1f} MB)")


def test_no_faulty_objects(save: AsaSave, dumper):
    # faulty_objects is an int counter (incremented per failed parse in
    # save_connection). It is final because the `save` fixture parses every
    # object during setup. Each failing object is captured under debug_dumps/
    # (binary + structured print + names + reparse.py) by the dumper fixture.
    count = save.faulty_objects
    print(f"Faulty objects: {count}")
    if dumper.dumped:
        print(f"Failed objects dumped for debugging under {DEBUG_DIR}:")
        for path in dumper.dumped:
            print(f"  - {path}  (run its reparse.py to iterate)")
    assert count == 0, (
        f"{count} objects failed to parse. See debug_dumps/ for each one "
        f"(binary + structured_print.txt + reparse.py), and the [error]/[parser] "
        f"logs above for the offending blueprints."
    )


def test_game_time(save: AsaSave, snapshot: Snapshot):
    ctx = save.save_context
    print(f"Map: {ctx.map_name}  Day: {ctx.current_day}  Time: {ctx.current_time}")
    assert ctx.current_time != 0, "current_time is 0"
    assert ctx.current_day != 0, "current_day is 0"
    snapshot.check("map_name", str(ctx.map_name))


def test_game_object_count(save: AsaSave, snapshot: Snapshot):
    objects = save.get_game_objects()
    print(f"Total game objects: {len(objects)}")
    assert len(objects) > 0, "Expected at least one game object"
    snapshot.check("game_objects", len(objects))


def test_general_api(save: AsaSave, snapshot: Snapshot):
    start = time.time()
    api = GeneralApi(save)
    objects = api.get_all_objects()
    elapsed = time.time() - start
    print(f"GeneralApi.get_all_objects(): {len(objects)} in {elapsed:.2f}s")
    assert len(objects) > 0
    snapshot.check("general_api_objects", len(objects))


def test_reparse_is_stable(save_file, snapshot: Snapshot):
    """Parse the save from scratch a few more times and require identical results.

    One clean parse is not evidence the parser is correct. On free-threaded
    builds ``get_game_objects()`` fans out over a ThreadPoolExecutor that shares
    a single SaveContext, so state races only bite in *some* runs — a shared
    ``generate_unknown`` flag used to fail roughly half of them while the
    testbench, parsing once, reported faulty=0. Parser state that leaks between
    parses (class-level counters, name-table pollution) surfaces here too.

    Runs are configurable: ``TESTBENCH_REPARSE_RUNS=0`` skips, default 3.
    """
    runs = int(os.environ.get("TESTBENCH_REPARSE_RUNS", "3"))
    if runs <= 0:
        pytest.skip("TESTBENCH_REPARSE_RUNS=0")

    if _PARALLEL_ENABLED:
        print(f"parallel parsing is ON; re-parsing {runs}x to shake out races")
    else:
        print(f"parallel parsing is OFF (GIL build) — re-parsing {runs}x still "
              f"catches state leaking between parses, but not thread races. "
              f"Run the bench on a free-threaded build to cover those.")

    counts = []
    for i in range(runs):
        s = AsaSave(save_file)
        try:
            objects = s.get_game_objects()
        except Exception as e:  # a parse that raised on run N but not run 1
            pytest.fail(f"re-parse {i + 1}/{runs} raised where the first parse did not: {e}")
        print(f"  re-parse {i + 1}/{runs}: {len(objects)} objects, faulty={s.faulty_objects}")
        assert s.faulty_objects == 0, (
            f"re-parse {i + 1}/{runs}: {s.faulty_objects} faulty object(s) "
            f"(the first parse had none) — parsing is not deterministic"
        )
        counts.append(len(objects))
        del s, objects
        gc.collect()

    assert len(set(counts)) == 1, (
        f"object count varies across parses: {counts}. Parsing is "
        f"nondeterministic — suspect mutable state shared by the worker threads."
    )
    # Same metric as test_game_object_count, so a re-parse that quietly returns a
    # different number of objects than the session parse fails against the baseline.
    snapshot.check("game_objects", counts[0])


def test_unresolved_names(save: AsaSave, snapshot: Snapshot):
    """Count the names arkparse had to invent to finish the parse.

    When a name id is missing from the save's name table, the parser fabricates
    an ``Unknown_<id>`` entry rather than failing (inside cryopod/custom-item
    data, where ids are genuinely local to the embedded blob). These are silent:
    they raise nothing and never count as faulty objects, yet each one is a name
    the parser could not resolve. Snapshotting the count keeps it from creeping
    up unnoticed when a format changes.
    """
    names = save.save_context.names
    unresolved = sorted(n for n in names.values() if isinstance(n, str) and n.startswith("Unknown_"))
    print(f"Unresolved (fabricated) names: {len(unresolved)} of {len(names)} total")
    for name in unresolved[:10]:
        print(f"  - {name}")
    if len(unresolved) > 10:
        print(f"  ... and {len(unresolved) - 10} more")
    snapshot.check("unresolved_names", len(unresolved))
