"""
Break down where SaveConnection.get_game_objects() spends its time during the
*selection* phase (everything before objects are actually parsed).

It replays the same loop stage by stage against the real save so each stage's
cost can be attributed:

    sql       pulling (key, value) rows out of SQLite
    uuid      byte_array_to_uuid per row
    all_uuids save_context.all_uuids.append per row
    read_name ArkBinaryParser + ArkGameObject.read_name per row
    classes   the `if class_name not in objects` dead-code list scan
    bp_filter the blueprint_name_filter lambda
    pattern   contains_any_pattern (the property_names byte scan)

Also times a SQL-side `instr(value, ?)` prefilter as an alternative to doing the
byte scan in Python.

Usage:
    python wip/profiling/profile_object_scan.py [path/to/Map_WP.ark] [--prop StructureID]
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from arkparse import AsaSave
from arkparse.api.dino_api import DinoApi
from arkparse.logging import ArkSaveLogger
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.parsing._fast_shim import contains_any_pattern
from arkparse.saves.save_connection import SaveConnection

REPO_ROOT = Path(__file__).resolve().parents[2]


def _default_save() -> Path:
    testbench = REPO_ROOT / "testbench" / "test_save"
    if testbench.exists():
        found = sorted(testbench.rglob("*.ark"))
        if found:
            return found[0]
    return REPO_ROOT / "tests" / "test_data" / "set_1" / "Ragnarok_WP" / "Ragnarok_WP.ark"


class Timer:
    def __init__(self):
        self.totals: dict[str, float] = {}

    def add(self, name: str, seconds: float) -> None:
        self.totals[name] = self.totals.get(name, 0.0) + seconds

    def report(self, rows: int) -> None:
        total = sum(self.totals.values())
        print(f"  {'stage':<12} {'seconds':>9} {'share':>7}   {'us/row':>8}")
        for name, secs in sorted(self.totals.items(), key=lambda kv: kv[1], reverse=True):
            print(f"  {name:<12} {secs:9.3f} {secs / total * 100:6.1f}%   {secs / rows * 1e6:8.2f}")
        print(f"  {'TOTAL':<12} {total:9.3f}")


def profile_scan(save_path: Path, prop: str) -> None:
    save = AsaSave(save_path)
    conn: SaveConnection = save.save_connection
    ctx = save.save_context

    prop_id = ctx.get_name_id(prop)
    if prop_id is None:
        raise SystemExit(f"Property {prop!r} is not in this save's name table")
    prop_ids = [prop_id.to_bytes(4, byteorder="little") + b"\x00\x00\x00\x00"]

    bp_filter = DinoApi._DEFAULT_CONFIG.blueprint_name_filter

    t = Timer()
    rows = 0
    matched_pattern = 0
    matched_bp = 0
    classes_list: list[str] = []
    all_uuids: list = []
    total_bytes = 0

    start_all = time.perf_counter()
    cursor = conn.connection.execute("SELECT key, value FROM game")
    while True:
        t0 = time.perf_counter()
        batch = cursor.fetchmany(2000)
        t.add("sql", time.perf_counter() - t0)
        if not batch:
            break

        for key, value in batch:
            rows += 1
            total_bytes += len(value)

            t0 = time.perf_counter()
            obj_uuid = SaveConnection.byte_array_to_uuid(key)
            t.add("uuid", time.perf_counter() - t0)

            t0 = time.perf_counter()
            all_uuids.append(obj_uuid)
            t.add("all_uuids", time.perf_counter() - t0)

            t0 = time.perf_counter()
            byte_buffer = ArkBinaryParser(value, ctx)
            class_name, *_ = ArkGameObject.read_name(obj_uuid, byte_buffer)
            t.add("read_name", time.perf_counter() - t0)

            t0 = time.perf_counter()
            if class_name not in classes_list:
                classes_list.append(class_name)
            t.add("classes", time.perf_counter() - t0)

            t0 = time.perf_counter()
            if bp_filter(class_name):
                matched_bp += 1
            t.add("bp_filter", time.perf_counter() - t0)

            t0 = time.perf_counter()
            if contains_any_pattern(value, prop_ids):
                matched_pattern += 1
            t.add("pattern", time.perf_counter() - t0)

    wall = time.perf_counter() - start_all

    print(f"\nrows={rows}  blob bytes={total_bytes / 1e6:.1f} MB  distinct classes={len(classes_list)}")
    print(f"{prop} pattern matches={matched_pattern}   dino bp filter matches={matched_bp}")
    print(f"instrumented wall time: {wall:.2f}s (timer overhead inflates this; use the shares)\n")
    t.report(rows)

    # --- Alternative: let SQLite do the byte scan --------------------------- #
    print("\nSQL-side prefilter (instr(value, ?) > 0):")
    t0 = time.perf_counter()
    cur = conn.connection.execute(
        "SELECT key, value FROM game WHERE instr(value, ?) > 0", (prop_ids[0],)
    )
    sql_rows = cur.fetchall()
    sql_time = time.perf_counter() - t0
    print(f"  {len(sql_rows)} rows in {sql_time:.2f}s")

    print("\nBaseline: pull every row out of SQLite and do nothing else:")
    t0 = time.perf_counter()
    n = 0
    cur = conn.connection.execute("SELECT key, value FROM game")
    for _ in cur:
        n += 1
    print(f"  {n} rows in {time.perf_counter() - t0:.2f}s")

    save.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("save", nargs="?", type=Path, default=None)
    parser.add_argument("--prop", default="StructureID")
    args = parser.parse_args()

    save_path = args.save or _default_save()
    if not save_path.exists():
        raise SystemExit(f"Save not found: {save_path}")

    ArkSaveLogger.disable_all_logs()
    ArkSaveLogger.allow_invalid_objects(True)
    ArkSaveLogger.allow_invalid_mod_objects(True)

    print(f"Save: {save_path}")
    profile_scan(save_path, args.prop)


if __name__ == "__main__":
    main()
