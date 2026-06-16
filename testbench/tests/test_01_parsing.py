"""Core parsing: the save loads, has no faulty objects, exposes game time,
and the general object API returns a stable object count."""
import time

from arkparse import AsaSave
from arkparse.api.general_api import GeneralApi

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
