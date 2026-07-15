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
        ArkMap.RAGNAROK: 205718,
        ArkMap.ABERRATION: 111674,
        ArkMap.EXTINCTION: 186879,
        ArkMap.ASTRAEOS: 425319,
        ArkMap.SCORCHED_EARTH: 98898,
        ArkMap.THE_ISLAND: 333884,
        ArkMap.THE_CENTER: 380535,
        ArkMap.LOST_COLONY: 132210,
        ArkMap.VALGUERO: 144419,
        ArkMap.GENESIS: 98948,
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

def test_retrieving_all_objects(map_save, objects_per_map: dict):
    """
    Test to retrieve all objects from the save file of the current map.
    """
    map_name, save = map_save
    retrieve_for_map(save, map_name, objects_per_map)

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
    api = GeneralApi(save)
    objects = api.get_all_objects()
    end_time = time.time()

    # Budget the time on the object count. Maps without an explicit (non-zero)
    # expectation fall back to the actual retrieved count.
    allowed_time = allowed_api_time(max(objects_per_map.get(map_name, 0), len(objects)))
    print(f"Retrieved {len(objects)} objects from {map_name.name.title()} save in {end_time - start_time:.2f} seconds.")

    # assert len(objects) == objects_per_map[map_name], f"Expected {objects_per_map[map_name]} objects, but got {len(objects)}"
    assert end_time - start_time < allowed_time, f"Retrieval took too long ({end_time - start_time:.3f} seconds), check object caching"

def test_retrieving_objects_through_api(map_save, objects_per_map: dict):
    """
    Test to retrieve objects from the save file of the current map using the API.
    """
    map_name, save = map_save
    retrieve_with_api(save, map_name, objects_per_map)

def test_game_time_retrieval(map_save):
    """
    Test to retrieve game time information from the current map save.
    """
    _, save = map_save
    save: AsaSave
    assert save.save_context.current_time != 0, f"Game time for {save.save_context.map_name} is 0"
    assert save.save_context.current_day != 0, f"Game day for {save.save_context.map_name} is 0"
    print(f"Map: {save.save_context.map_name}, Current Time: {save.save_context.current_time}, Current Day: {save.save_context.current_day}")