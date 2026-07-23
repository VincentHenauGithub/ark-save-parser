from typing import List
import pytest
import gc
from pathlib import Path
import shutil
from uuid import uuid4

from arkparse import AsaSave
from arkparse.enums import ArkMap
from arkparse.logging import ArkSaveLogger

ArkSaveLogger.disable_all_logs()
# ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.WARNING, True)
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.ERROR, True)
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.INFO, True)
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.DEBUG, True)
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.WARNING, True)
ArkSaveLogger.allow_invalid_objects(False)
CURRENT_SET = "1"

def file_directory(set: str) -> Path:
    """
    Returns the directory of the current file.
    """
    return Path(__file__).parent / "test_data" / set

def save_path(map: ArkMap, set: str = "set_" + CURRENT_SET):
    """
    Returns the path to the save file for the given map.
    """
    return file_directory(set) / f"{map.to_file_name()}_WP" / f"{map.to_file_name()}_WP.ark"

@pytest.fixture(scope="session")
def base_save_path() -> Path:
    """
    Returns the base path to the save files.
    """
    return Path(__file__).parent / "test_data"

def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--profile",
        action="store",
        default="simple",
        choices=["simple", "full"],
        help="Which test profile to run (simple: only Ragnarok; full: all maps)",
    )

@pytest.fixture(scope="session")
def profile(request: pytest.FixtureRequest):
    return request.config.getoption("profile")

@pytest.fixture(scope="session")
def resource_path() -> Path:
    """
    Returns the path to the resource directory.
    """
    return Path(__file__).parent / "test_data"

@pytest.fixture(scope="session")
def session_uuid() -> str:
    """
    Returns a unique identifier for the session.
    """
    return str(uuid4())

@pytest.fixture(scope="session", autouse=True)
def temp_file_folder(session_uuid):
    """
    Creates a clean temp_files folder *once* before any tests run,
    and then deletes it *once* after the very last test completes.
    """
    path = Path(__file__).parent / f"temp_files_{session_uuid}"

    # SETUP: remove any existing folder
    if path.exists():
        shutil.rmtree(path)

    # (re-)create it fresh
    path.mkdir(parents=True, exist_ok=True)

    # yield it for tests to use…
    yield path

    # TEARDOWN: after *all* tests have finished, delete it
    if path.exists():
        shutil.rmtree(path)

# Ragnarok is listed first so that the Ragnarok-specific tests (which run only for
# Ragnarok) coalesce with the generic Ragnarok parametrization into a single group,
# so the Ragnarok save is loaded and disposed exactly once.
_FULL_PROFILE_MAPS = [
    ArkMap.RAGNAROK,
    ArkMap.ABERRATION,
    ArkMap.EXTINCTION,
    ArkMap.SCORCHED_EARTH,
    ArkMap.THE_CENTER,
    ArkMap.THE_ISLAND,
    ArkMap.ASTRAEOS,
    ArkMap.LOST_COLONY,
    ArkMap.VALGUERO,
    ArkMap.GENESIS,
    ArkMap.DEIMOS_MAP,
]

def _profile_maps(profile: str) -> List[ArkMap]:
    if profile == "simple":
        return [ArkMap.RAGNAROK]
    return list(_FULL_PROFILE_MAPS)

@pytest.fixture(scope="session")
def enabled_maps(profile):
    return _profile_maps(profile)

def _dispose_save(save: AsaSave):
    """
    Release a save's parsed objects and database handle so its memory is
    reclaimed before the next map is loaded. The heavy state lives in the
    connection's `parsed_objects` cache; clearing it (and forcing a GC) is what
    actually frees memory — `close()` alone only drops the SQLite handle.
    """
    try:
        conn = getattr(save, "save_connection", None)
        if conn is not None and getattr(conn, "parsed_objects", None) is not None:
            conn.parsed_objects.clear()
        if getattr(save, "parsed_objects", None) is not None:
            save.parsed_objects.clear()
        save.game_obj_binaries = None
        save.close()
    finally:
        gc.collect()

def pytest_generate_tests(metafunc):
    """
    Drive the memory-efficient, one-save-at-a-time execution model.

    Any test that needs `map_save` (directly, or transitively via a fixture such
    as `ragnarok_save`) is parametrized over the enabled maps. Because
    `map_save` is session-scoped, pytest groups every test sharing a map value
    together and tears the save down — via `_dispose_save` — before setting up
    the next map, so only one save is resident at a time.

    Tests that need `ragnarok_save` are Ragnarok-specific (exact counts, item
    generation, players) and are restricted to the Ragnarok parametrization.
    """
    if "map_save" not in metafunc.fixturenames:
        return
    all_maps = _profile_maps(metafunc.config.getoption("profile"))
    if "ragnarok_save" in metafunc.fixturenames:
        maps = [m for m in all_maps if m == ArkMap.RAGNAROK]
    else:
        maps = all_maps
    metafunc.parametrize("map_save", maps, indirect=True, ids=[m.name for m in maps])

@pytest.fixture(scope="session")
def map_save(request):
    """
    Yields a single `(ArkMap, AsaSave)` for the parametrized map. The save is
    disposed on teardown — before the next parametrized map is set up — keeping
    peak memory usage to a single save.
    """
    map: ArkMap = request.param
    save = AsaSave(save_path(map))
    save.set_map(map)
    yield map, save
    _dispose_save(save)

@pytest.fixture(scope="session")
def ragnarok_save(map_save):
    # Only reached under the Ragnarok parametrization (see pytest_generate_tests).
    _, save = map_save
    return save

@pytest.fixture(scope="session")
def rag_limited():
    # Distinct, small save set ("set_2"), independent of the map_save cycle.
    resource = AsaSave(save_path(ArkMap.RAGNAROK, "set_2"))
    yield resource
    _dispose_save(resource)
