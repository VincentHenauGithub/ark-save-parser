"""
Testbench conftest.

Drop an ARK save (the ``<Map>_WP`` folder, or just its ``.ark`` file) anywhere
under ``testbench/test_save/`` and run ``pytest`` from this directory. The save is
autodetected recursively, parsed once per session, and exercised by every test.

Assertions are snapshot-based: counts are recorded on the first run and compared
on later runs (see snapshot.py). No map-specific expected values are hardcoded, so
any save works.
"""
from __future__ import annotations

import shutil

import pytest
from pathlib import Path

from arkparse import AsaSave
from arkparse.logging import ArkSaveLogger

from snapshot import Snapshot
from debug import FailedObjectDumper, DEBUG_DIR

# --------------------------------------------------------------------------- #
# Logging: errors/warnings on, the noisy levels off, strict object validation.
# --------------------------------------------------------------------------- #
ArkSaveLogger.disable_all_logs()
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.ERROR, True)
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.WARNING, True)
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.INFO, True)
ArkSaveLogger.allow_invalid_objects(False)
# Also hard-fail on mod-namespace objects (not just /Game/ & /Script/). Set to
# True if your save uses mods arkparse can't fully parse and you want to proceed.
ArkSaveLogger.allow_invalid_mod_objects(False)

TEST_SAVE_DIR = Path(__file__).parent / "test_save"


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--update-snapshot",
        action="store_true",
        default=False,
        help="Overwrite stored snapshot metrics with the current run's values.",
    )


def _find_ark_save() -> Path | None:
    """Locate the first .ark file anywhere under test_save/."""
    if not TEST_SAVE_DIR.exists():
        return None
    matches = sorted(TEST_SAVE_DIR.rglob("*.ark"))
    return matches[0] if matches else None


@pytest.fixture(scope="session")
def save_file() -> Path:
    path = _find_ark_save()
    if path is None:
        pytest.skip(
            f"No .ark save found under {TEST_SAVE_DIR}. "
            "Drop a save (or its folder) there and re-run."
        )
    print(f"\nUsing save file: {path}")
    return path


@pytest.fixture(scope="session")
def dumper():
    """Registers the failed-object dumper and clears last run's dumps.

    Every object that fails to parse is captured to ``debug_dumps/`` (binary +
    structured print + names + a standalone reparse.py). See debug.py.
    """
    if DEBUG_DIR.exists():
        shutil.rmtree(DEBUG_DIR)
    d = FailedObjectDumper()
    ArkSaveLogger.set_object_failure_handler(d)
    yield d
    ArkSaveLogger.set_object_failure_handler(None)


@pytest.fixture(scope="session")
def save(save_file: Path, dumper: FailedObjectDumper) -> AsaSave:
    """The parsed save, shared across the whole session (parsed once).

    Parsing is done in two phases so that *all* failures are captured in one run:

    1. Parse with mod failures allowed so every failing object is dumped to
       ``debug_dumps/`` (rather than aborting at the first one).
    2. If anything failed, raise a clean summary pointing at the dumps. This
       errors the fixture, and with ``-x`` the run stops here with the structured
       parser logs and dump paths right above.
    """
    # The reparse.py helpers reload from the save, so the dumper needs its path.
    dumper.save_path = save_file

    s = AsaSave(save_file)
    print("\n[testbench] parsing all game objects (flushes parser logs)...")

    # Phase 1: allow mod failures so the dumper sees every one.
    ArkSaveLogger.allow_invalid_mod_objects(True)
    objects = s.get_game_objects()
    ArkSaveLogger.allow_invalid_mod_objects(False)

    faulty = s.faulty_objects
    print(f"[testbench] parsed {len(objects)} objects, faulty={faulty}")

    if dumper.dumped:
        print(f"[testbench] {len(dumper.dumped)} failed object(s) dumped under {DEBUG_DIR}:")
        for path in dumper.dumped:
            print(f"  - {path}")
    return s


@pytest.fixture(scope="session")
def save_key(save_file: Path, save: AsaSave) -> str:
    """A stable identity for this save, used to name its snapshot file."""
    try:
        map_name = str(save.save_context.map_name)
    except Exception:
        map_name = "unknown"
    size = save_file.stat().st_size
    safe_map = "".join(c if c.isalnum() else "_" for c in map_name)
    return f"{safe_map}_{size}"


@pytest.fixture(scope="session")
def snapshot(save_key: str, request: pytest.FixtureRequest):
    """Session-scoped snapshot; flushed once after all tests complete."""
    snap = Snapshot(save_key, update=request.config.getoption("--update-snapshot"))
    yield snap
    snap.flush()
