from typing import Dict
import pytest
import time

from arkparse import AsaSave
from arkparse.enums import ArkMap
from arkparse.api.general_api import GeneralApi

@pytest.fixture(scope="module")
def objects_per_map():
    """ Fixture to provide the expected number of objects for each map. """
    return {
        ArkMap.RAGNAROK: 203508,
        ArkMap.ABERRATION: 110747,
        ArkMap.EXTINCTION: 185646,
        ArkMap.ASTRAEOS: 421101,
        ArkMap.SCORCHED_EARTH: 98219,
        ArkMap.THE_ISLAND: 331301,
        ArkMap.THE_CENTER: 377294
    }

######################################################################################
## Tests for retrieving all objects from save files for different maps with AsaSave ##
######################################################################################

def retrieve_for_map(save: AsaSave, map_name: ArkMap, objects_per_map: dict):
    """
    Helper function to retrieve all objects from a save file for a specific map.
    """
    assert isinstance(save, AsaSave), f"Expected AsaSave, got {type(save)}"
    objects = save.get_game_objects()
    print(f"Total objects in {map_name.name.title()} save: {len(objects)}")
    # assert len(objects) == objects_per_map[map_name], f"Expected {objects_per_map[map_name]} objects, got {len(objects)}"
    assert save.faulty_objects == 0, f"There are {save.faulty_objects} faultily parsed objects in the save file"

def test_retrieving_all_ragnarok_objects(ragnarok_save: AsaSave, objects_per_map: dict, enabled_maps: list):
    """
    Test to retrieve all objects from a Ragnarok save file.
    """
    if not ArkMap.RAGNAROK in enabled_maps:
        pytest.skip("Ragnarok map is not enabled in the test configuration.")
    retrieve_for_map(ragnarok_save, ArkMap.RAGNAROK, objects_per_map)

def test_retrieving_all_aberration_objects(aberration_save: AsaSave, objects_per_map: dict, enabled_maps: list):
    """
    Test to retrieve all objects from an Aberration save file.
    """
    if not ArkMap.ABERRATION in enabled_maps:
        pytest.skip("Aberration map is not enabled in the test configuration.")
    retrieve_for_map(aberration_save, ArkMap.ABERRATION, objects_per_map)

def test_retrieving_all_extinction_objects(extinction_save: AsaSave, objects_per_map: dict, enabled_maps: list):
    """
    Test to retrieve all objects from an Extinction save file.
    """
    if not ArkMap.EXTINCTION in enabled_maps:
        pytest.skip("Extinction map is not enabled in the test configuration.")
    retrieve_for_map(extinction_save, ArkMap.EXTINCTION, objects_per_map)

def test_retrieving_all_astraeos_objects(astraeos_save: AsaSave, objects_per_map: dict, enabled_maps: list):
    """
    Test to retrieve all objects from an Astraeos save file.
    """
    if not ArkMap.ASTRAEOS in enabled_maps:
        pytest.skip("Astraeos map is not enabled in the test configuration.")
    retrieve_for_map(astraeos_save, ArkMap.ASTRAEOS, objects_per_map)

def test_retrieving_all_scorched_earth_objects(scorched_earth_save: AsaSave, objects_per_map: dict, enabled_maps: list):
    """
    Test to retrieve all objects from a Scorched Earth save file.
    """
    if not ArkMap.SCORCHED_EARTH in enabled_maps:
        pytest.skip("Scorched Earth map is not enabled in the test configuration.")
    retrieve_for_map(scorched_earth_save, ArkMap.SCORCHED_EARTH, objects_per_map)

def test_retrieving_all_the_island_objects(the_island_save: AsaSave, objects_per_map: dict, enabled_maps: list):
    """
    Test to retrieve all objects from a The Island save file.
    """
    if not ArkMap.THE_ISLAND in enabled_maps:
        pytest.skip("The Island map is not enabled in the test configuration.")
    retrieve_for_map(the_island_save, ArkMap.THE_ISLAND, objects_per_map)

def test_retrieving_all_the_center_objects(the_center_save: AsaSave, objects_per_map: dict, enabled_maps: list):
    """
    Test to retrieve all objects from a The Center save file.
    """
    if not ArkMap.THE_CENTER in enabled_maps:
        pytest.skip("The Center map is not enabled in the test configuration.")
    retrieve_for_map(the_center_save, ArkMap.THE_CENTER, objects_per_map)

#######################################################################################
######## Tests for retrieving specific objects from save files using the API ##########
#######################################################################################

def allowed_api_time(nr_of_objects: int) -> float:
    """
    Calculate the allowed API time based on the number of objects.
    This is a simple heuristic to ensure the API can handle the load.
    """
    microseconds_per_object = 150
    seconds_per_object = microseconds_per_object / 1_000_000
    return seconds_per_object * nr_of_objects

def retrieve_with_api(save: AsaSave, map_name: ArkMap, objects_per_map: dict):
    """
    Helper function to retrieve all objects from a save file for a specific map using the API.
    """
    start_time = time.time()
    allowed_time = allowed_api_time(objects_per_map[map_name])
    api = GeneralApi(save)
    objects = api.get_all_objects()
    end_time = time.time()
    print(f"Retrieved {len(objects)} objects from {map_name.name.title()} save in {end_time - start_time:.2f} seconds.")

    # assert len(objects) == objects_per_map[map_name], f"Expected {objects_per_map[map_name]} objects, but got {len(objects)}"
    assert end_time - start_time < allowed_time, f"Retrieval took too long ({end_time - start_time:.3f} seconds), check object caching"

def test_retrieving_ragnarok_object_through_api(ragnarok_save: AsaSave, objects_per_map: dict, enabled_maps: list):
    """
    Test to retrieve a specific object from a Ragnarok save file using the API.
    """
    if not ArkMap.RAGNAROK in enabled_maps:
        pytest.skip("Ragnarok map is not enabled in the test configuration.")
    retrieve_with_api(ragnarok_save, ArkMap.RAGNAROK, objects_per_map)

def test_retrieving_aberration_object_through_api(aberration_save: AsaSave, objects_per_map: dict, enabled_maps: list):
    """
    Test to retrieve a specific object from an Aberration save file using the API.
    """
    if not ArkMap.ABERRATION in enabled_maps:
        pytest.skip("Aberration map is not enabled in the test configuration.")
    retrieve_with_api(aberration_save, ArkMap.ABERRATION, objects_per_map)

def test_retrieving_extinction_object_through_api(extinction_save: AsaSave, objects_per_map: dict, enabled_maps: list):
    """
    Test to retrieve a specific object from an Extinction save file using the API.
    """
    if not ArkMap.EXTINCTION in enabled_maps:
        pytest.skip("Extinction map is not enabled in the test configuration.")
    retrieve_with_api(extinction_save, ArkMap.EXTINCTION, objects_per_map)

def test_retrieving_astraeos_object_through_api(astraeos_save: AsaSave, objects_per_map: dict, enabled_maps: list):
    """
    Test to retrieve a specific object from an Astraeos save file using the API.
    """
    if not ArkMap.ASTRAEOS in enabled_maps:
        pytest.skip("Astraeos map is not enabled in the test configuration.")
    retrieve_with_api(astraeos_save, ArkMap.ASTRAEOS, objects_per_map)

def test_retrieving_scorched_earth_object_through_api(scorched_earth_save: AsaSave, objects_per_map: dict, enabled_maps: list):
    """
    Test to retrieve a specific object from a Scorched Earth save file using the API.
    """
    if not ArkMap.SCORCHED_EARTH in enabled_maps:
        pytest.skip("Scorched Earth map is not enabled in the test configuration.")
    retrieve_with_api(scorched_earth_save, ArkMap.SCORCHED_EARTH, objects_per_map)

def test_retrieving_the_island_object_through_api(the_island_save: AsaSave, objects_per_map: dict, enabled_maps: list):
    """
    Test to retrieve a specific object from a The Island save file using the API.
    """
    if not ArkMap.THE_ISLAND in enabled_maps:
        pytest.skip("The Island map is not enabled in the test configuration.")

    retrieve_with_api(the_island_save, ArkMap.THE_ISLAND, objects_per_map)

def test_retrieving_the_center_object_through_api(the_center_save: AsaSave, objects_per_map: dict, enabled_maps: list):
    """
    Test to retrieve a specific object from a The Center save file using the API.
    """
    if not ArkMap.THE_CENTER in enabled_maps:
        pytest.skip("The Center map is not enabled in the test configuration.")
    retrieve_with_api(the_center_save, ArkMap.THE_CENTER, objects_per_map)

def test_game_time_retrieval(enabled_map_objects: Dict[ArkMap, AsaSave]):
    """
    Test to retrieve game time information from all enabled map saves.
    """
    print("\nGame Time Retrieval:")
    for _, save in enabled_map_objects.items():
        save: AsaSave
        assert save.save_context.current_time != 0, f"Game time for {save.save_context.map_name} is 0"
        assert save.save_context.current_day != 0, f"Game day for {save.save_context.map_name} is 0"
        print(f"Map: {save.save_context.map_name}, Current Time: {save.save_context.current_time}, Current Day: {save.save_context.current_day}")