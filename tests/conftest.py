from typing import Dict, List
import pytest
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

@pytest.fixture(scope="session")
def enabled_maps(profile):
    if profile == "simple":
        return [ArkMap.RAGNAROK]
    elif profile == "full":
        return [
            ArkMap.ABERRATION,
            ArkMap.EXTINCTION,
            ArkMap.RAGNAROK,
            ArkMap.SCORCHED_EARTH,
            ArkMap.THE_CENTER,
            ArkMap.THE_ISLAND,
            ArkMap.ASTRAEOS,
            ArkMap.LOST_COLONY,
            ArkMap.VALGUERO,
            ArkMap.GENESIS,
        ]
    
@pytest.fixture(scope="session")
def ragnarok_save(enabled_maps):
    # setup (runs once, at first use)
    if ArkMap.RAGNAROK not in enabled_maps:
        pytest.skip("Ragnarok map is not enabled in the test configuration.")
    resource = AsaSave(save_path(ArkMap.RAGNAROK))
    yield resource

@pytest.fixture(scope="session")
def rag_limited():
    # setup (runs once, at first use)
    resource = AsaSave(save_path(ArkMap.RAGNAROK, "set_2"))
    yield resource

@pytest.fixture(scope="session")
def aberration_save(enabled_maps):
    # setup (runs once, at first use)
    if ArkMap.ABERRATION not in enabled_maps:
        pytest.skip("Aberration map is not enabled in the test configuration.")
    resource = AsaSave(save_path(ArkMap.ABERRATION))
    yield resource

@pytest.fixture(scope="session")
def extinction_save(enabled_maps):
    # setup (runs once, at first use)
    if ArkMap.EXTINCTION not in enabled_maps:
        pytest.skip("Extinction map is not enabled in the test configuration.")
    resource = AsaSave(save_path(ArkMap.EXTINCTION))
    yield resource

@pytest.fixture(scope="session")
def astraeos_save(enabled_maps):
    # setup (runs once, at first use)
    if ArkMap.ASTRAEOS not in enabled_maps:
        pytest.skip("Astraeos map is not enabled in the test configuration.")
    resource = AsaSave(save_path(ArkMap.ASTRAEOS))
    yield resource

@pytest.fixture(scope="session")
def scorched_earth_save(enabled_maps):
    # setup (runs once, at first use)
    if ArkMap.SCORCHED_EARTH not in enabled_maps:
        pytest.skip("Scorched Earth map is not enabled in the test configuration.")
    resource = AsaSave(save_path(ArkMap.SCORCHED_EARTH))
    yield resource

@pytest.fixture(scope="session")
def the_island_save(enabled_maps):
    # setup (runs once, at first use)
    if ArkMap.THE_ISLAND not in enabled_maps:
        pytest.skip("The Island map is not enabled in the test configuration.")
    resource = AsaSave(save_path(ArkMap.THE_ISLAND))
    yield resource

@pytest.fixture(scope="session")
def the_center_save(enabled_maps):
    # setup (runs once, at first use)
    if ArkMap.THE_CENTER not in enabled_maps:
        pytest.skip("The Center map is not enabled in the test configuration.")
    resource = AsaSave(save_path(ArkMap.THE_CENTER))
    yield resource

@pytest.fixture(scope="session")
def enabled_map_objects(enabled_maps):
    enabled: Dict[ArkMap, AsaSave] = {}
    if ArkMap.RAGNAROK in enabled_maps:
        enabled[ArkMap.RAGNAROK] = AsaSave(save_path(ArkMap.RAGNAROK))
    if ArkMap.ABERRATION in enabled_maps:
        enabled[ArkMap.ABERRATION] = AsaSave(save_path(ArkMap.ABERRATION))
    if ArkMap.EXTINCTION in enabled_maps:
        enabled[ArkMap.EXTINCTION] = AsaSave(save_path(ArkMap.EXTINCTION))
    if ArkMap.ASTRAEOS in enabled_maps:
        enabled[ArkMap.ASTRAEOS] = AsaSave(save_path(ArkMap.ASTRAEOS))
    if ArkMap.SCORCHED_EARTH in enabled_maps:
        enabled[ArkMap.SCORCHED_EARTH] = AsaSave(save_path(ArkMap.SCORCHED_EARTH))
    if ArkMap.THE_ISLAND in enabled_maps:
        enabled[ArkMap.THE_ISLAND] = AsaSave(save_path(ArkMap.THE_ISLAND))
    if ArkMap.THE_CENTER in enabled_maps:
        enabled[ArkMap.THE_CENTER] = AsaSave(save_path(ArkMap.THE_CENTER))
    if ArkMap.LOST_COLONY in enabled_maps:
        enabled[ArkMap.LOST_COLONY] = AsaSave(save_path(ArkMap.LOST_COLONY))
    if ArkMap.VALGUERO in enabled_maps:
        enabled[ArkMap.VALGUERO] = AsaSave(save_path(ArkMap.VALGUERO))
    if ArkMap.GENESIS in enabled_maps:
        enabled[ArkMap.GENESIS] = AsaSave(save_path(ArkMap.GENESIS))
    
    yield enabled
