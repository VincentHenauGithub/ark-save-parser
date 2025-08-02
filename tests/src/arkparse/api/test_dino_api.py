import pytest
from pathlib import Path
from arkparse.api.dino_api import DinoApi
from arkparse import AsaSave
from arkparse.object_model.dinos import TamedDino, TamedBaby, BabyStage
from arkparse.enums import ArkMap

NR_DINOS = 33767
NR_TAMED = 2242
NR_WILD = 31525
NR_IN_CRYO = 1517
NR_WILD_BABIES = 2747
NR_TAMED_BABIES = 40
NR_BABIES = NR_WILD_BABIES + NR_TAMED_BABIES
NR_BABIES_IN_CRYO = 40

def dinos_per_map():
    """ Fixture to provide the expected number of dinos for each map. """
    return {
        ArkMap.RAGNAROK: NR_DINOS,
        ArkMap.ABERRATION: 21399,
        ArkMap.EXTINCTION: 17376,
        ArkMap.ASTRAEOS: 48959,
        ArkMap.SCORCHED_EARTH: 16096,
        ArkMap.THE_ISLAND: 26716,
        ArkMap.THE_CENTER: 36007
    }

@pytest.fixture(scope="module")
def dino_api(ragnarok_save):
    """
    Fixture to provide a DinoApi instance for the Ragnarok save.
    """
    resource = DinoApi(ragnarok_save)
    yield resource

@pytest.fixture(scope="module")
def dino_mod_api(rag_limited: AsaSave, temp_file_folder: Path):
    """
    Helper function to get the DinoApi instance for the rag_limited save.
    """
    rag_limited.store_db(temp_file_folder / "copy.db")
    assert (temp_file_folder / "copy.db").exists(), "Database file should be created"
    print(f"Database stored at {temp_file_folder / 'copy.db'}")
    save = AsaSave(path=temp_file_folder / "copy.db")
    assert save is not None, "AsaSave should be initialized"
    return DinoApi(save)

def test_parse_ragnarok(dino_api: DinoApi, enabled_maps: list):
    """
    Test to parse the Ragnarok save file and check the number of dinos.
    """
    if not ArkMap.RAGNAROK in enabled_maps:
        pytest.skip("Ragnarok map is not enabled in the test configuration.")
    dinos = dino_api.get_all()  # This will trigger the parsing of dinos
    print(f"Total dinos found in Ragnarok: {len(dinos)}")
    assert len(dinos) == dinos_per_map()[ArkMap.RAGNAROK], "Unexpected number of dinos found"

def test_parse_aberration(aberration_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Aberration save file and check the number of dinos.
    """
    if not ArkMap.ABERRATION in enabled_maps:
        pytest.skip("Aberration map is not enabled in the test configuration.")
    dinos = DinoApi(aberration_save).get_all()  # This will trigger the parsing of dinos
    print(f"Total dinos found in Aberration: {len(dinos)}")
    assert len(dinos) == dinos_per_map()[ArkMap.ABERRATION], "Unexpected number of dinos found"

def test_parse_extinction(extinction_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Extinction save file and check the number of dinos.
    """
    if not ArkMap.EXTINCTION in enabled_maps:
        pytest.skip("Extinction map is not enabled in the test configuration.")
    dinos = DinoApi(extinction_save).get_all()  # This will trigger the parsing of dinos
    print(f"Total dinos found in Extinction: {len(dinos)}")
    assert len(dinos) == dinos_per_map()[ArkMap.EXTINCTION], "Unexpected number of dinos found"

def test_parse_astraeos(astraeos_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Astraeos save file and check the number of dinos.
    """
    if not ArkMap.ASTRAEOS in enabled_maps:
        pytest.skip("Astraeos map is not enabled in the test configuration.")
    dinos = DinoApi(astraeos_save).get_all()  # This will trigger the parsing of dinos
    print(f"Total dinos found in Astraeos: {len(dinos)}")
    assert len(dinos) == dinos_per_map()[ArkMap.ASTRAEOS], "Unexpected number of dinos found"

def test_parse_scorched_earth(scorched_earth_save: AsaSave, enabled_maps: list):
    """
    Test to parse the Scorched Earth save file and check the number of dinos.
    """
    if not ArkMap.SCORCHED_EARTH in enabled_maps:
        pytest.skip("Scorched Earth map is not enabled in the test configuration.")
    dinos = DinoApi(scorched_earth_save).get_all()  # This will trigger the parsing of dinos
    print(f"Total dinos found in Scorched Earth: {len(dinos)}")
    assert len(dinos) == dinos_per_map()[ArkMap.SCORCHED_EARTH], "Unexpected number of dinos found"

def test_parse_the_island(the_island_save: AsaSave, enabled_maps: list):
    """
    Test to parse The Island save file and check the number of dinos.
    """
    if not ArkMap.THE_ISLAND in enabled_maps:
        pytest.skip("The Island map is not enabled in the test configuration.")
    dinos = DinoApi(the_island_save).get_all()  # This will trigger the parsing of dinos
    print(f"Total dinos found in The Island: {len(dinos)}")
    assert len(dinos) == dinos_per_map()[ArkMap.THE_ISLAND], "Unexpected number of dinos found"

def test_parse_the_center(the_center_save: AsaSave, enabled_maps: list):
    """
    Test to parse The Center save file and check the number of dinos.
    """
    if not ArkMap.THE_CENTER in enabled_maps:
        pytest.skip("The Center map is not enabled in the test configuration.")
    dinos = DinoApi(the_center_save).get_all()  # This will trigger the parsing of dinos
    print(f"Total dinos found in The Center: {len(dinos)}")
    assert len(dinos) == dinos_per_map()[ArkMap.THE_CENTER], "Unexpected number of dinos found"

def test_get_all_dinos(dino_api: DinoApi):
    """
    Test to retrieve all tamed dinos from the Ragnarok save.
    """
    dinos = dino_api.get_all()
    assert isinstance(dinos, dict), "Expected a dictionary of dinos"
    print(f"Total dinos found: {len(dinos)}")
    assert len(dinos) == NR_DINOS, f"Expected {NR_DINOS} dinos, got {len(dinos)}"

    nr_tamed = 0
    nr_wild = 0
    in_cryopod = 0
    in_cryopod_wild = 0
    for _, dino in dinos.items():
        if isinstance(dino, TamedDino):
            nr_tamed += 1
            if dino.is_cryopodded:
                in_cryopod += 1
        else:
            nr_wild += 1
            if dino.is_cryopodded:
                in_cryopod_wild += 1
    
    print(f"Total tamed dinos: {nr_tamed}, Total wild dinos: {nr_wild}")
    print(f"Tamed dinos in cryopods: {in_cryopod}, Wild dinos in cryopods: {in_cryopod_wild}")
    assert nr_tamed == NR_TAMED, f"Expected {NR_TAMED} tamed dinos, got {nr_tamed}"
    assert nr_wild == NR_WILD, f"Expected {NR_WILD} wild dinos, got {nr_wild}"
    assert in_cryopod_wild == 0, "There should be no wild dinos in cryopods"
    assert in_cryopod == NR_IN_CRYO, f"Expected {NR_IN_CRYO} tamed dinos in cryopods, got {in_cryopod}"

def test_retrieve_wild_dinos(dino_api: DinoApi):
    """
    Test to retrieve all wild dinos from the Ragnarok save.
    """
    wild_dinos = dino_api.get_all_wild()
    assert isinstance(wild_dinos, dict), "Expected a dictionary of wild dinos"
    print(f"Total wild dinos found: {len(wild_dinos)}")
    assert len(wild_dinos) == NR_WILD, f"Expected {NR_WILD} wild dinos, got {len(wild_dinos)}"

def test_retrieve_tamed_dinos(dino_api: DinoApi):
    """
    Test to retrieve all tamed dinos from the Ragnarok save.
    """
    tamed_dinos = dino_api.get_all_tamed()
    assert isinstance(tamed_dinos, dict), "Expected a dictionary of tamed dinos"
    print(f"Total tamed dinos found: {len(tamed_dinos)}")
    assert len(tamed_dinos) == NR_TAMED, f"Expected {NR_TAMED} tamed dinos, got {len(tamed_dinos)}"

def test_retrieve_uncryopodded_dinos(dino_api: DinoApi):
    """
    Test to retrieve all uncryopodded dinos from the Ragnarok save.
    """
    uncryopodded_dinos = dino_api.get_all_tamed(include_cryopodded=False)
    assert isinstance(uncryopodded_dinos, dict), "Expected a dictionary of uncryopodded dinos"
    print(f"Total uncryopodded dinos found: {len(uncryopodded_dinos)}")
    assert len(uncryopodded_dinos) == NR_TAMED - NR_IN_CRYO, f"Expected {NR_TAMED - NR_IN_CRYO} uncryopodded dinos, got {len(uncryopodded_dinos)}"

def test_retrieve_cryopodded_dinos(dino_api: DinoApi):
    """
    Test to retrieve all cryopodded dinos from the Ragnarok save.
    """
    cryopodded_dinos = dino_api.get_all_filtered(
        only_cryopodded=True,
    )

    assert isinstance(cryopodded_dinos, dict), "Expected a dictionary of cryopodded dinos"
    print(f"Total cryopodded dinos found: {len(cryopodded_dinos)}")
    assert len(cryopodded_dinos) == NR_IN_CRYO, f"Expected {NR_IN_CRYO} cryopodded dinos, got {len(cryopodded_dinos)}"

def test_retrieve_babies(dino_api: DinoApi):
    """ Test to retrieve all baby dinos from the Ragnarok save.
    """
    babies = dino_api.get_all_babies(include_tamed=True, include_cryopodded=True, include_wild=True)
    assert isinstance(babies, dict), "Expected a dictionary of baby dinos"
    print(f"Total baby dinos found: {len(babies)}")
    assert len(babies) == NR_BABIES, f"Expected {NR_BABIES} baby dinos, got {len(babies)}"

def test_retrieve_wild_babies(dino_api: DinoApi):
    """ Test to retrieve all wild baby dinos from the Ragnarok save.
    """
    wild_babies = dino_api.get_all_babies(include_tamed=False, include_cryopodded=True, include_wild=True)
    assert isinstance(wild_babies, dict), "Expected a dictionary of wild baby dinos"
    print(f"Total wild baby dinos found: {len(wild_babies)}")
    assert len(wild_babies) == NR_WILD_BABIES, f"Expected {NR_WILD_BABIES} wild baby dinos, got {len(wild_babies)}"

def test_retrieve_tamed_babies(dino_api: DinoApi):
    """ Test to retrieve all tamed baby dinos from the Ragnarok save.
    """
    tamed_babies = dino_api.get_all_babies(include_tamed=True, include_cryopodded=True, include_wild=False)
    assert isinstance(tamed_babies, dict), "Expected a dictionary of tamed baby dinos"
    print(f"Total tamed baby dinos found: {len(tamed_babies)}")
    assert len(tamed_babies) == NR_TAMED_BABIES, f"Expected {NR_TAMED_BABIES} tamed baby dinos, got {len(tamed_babies)}"

def test_retrieve_babies_in_cryopods(dino_api: DinoApi):
    """ Test to retrieve all baby dinos in cryopods from the Ragnarok save.
    """
    cryopodded_babies = dino_api.get_all_babies(include_tamed=True, include_cryopodded=True, include_wild=False)
    assert isinstance(cryopodded_babies, dict), "Expected a dictionary of cryopodded baby dinos"
    print(f"Total cryopodded baby dinos found: {len(cryopodded_babies)}")
    assert len(cryopodded_babies) == NR_BABIES_IN_CRYO, f"Expected {NR_BABIES_IN_CRYO} cryopodded baby dinos, got {len(cryopodded_babies)}"

def test_tamed_baby_stage(dino_api: DinoApi):
    """ Test to check the stage of a tamed baby dino.
    """
    babies = dino_api.get_all_babies(include_tamed=True, include_cryopodded=True, include_wild=False)
    assert isinstance(babies, dict), "Expected a dictionary of tamed baby dinos"
    
    for baby in babies.values():
        stage: BabyStage = baby.stage
        maturation: float = baby.percentage_matured
        imprinted: float = baby.percentage_imprinted
        print(f"Baby {baby.get_short_name()} is at stage {stage} with maturation {maturation:.2f}% and imprinted {imprinted:.2f}%")
        if stage == BabyStage.BABY:
            assert maturation < 10.0, "Baby stage should have maturation less than 10%"
        elif stage == BabyStage.JUVENILE:
            assert 10.0 <= maturation < 50.0, "Juvenile stage should have maturation between 10% and 50%"
        elif stage == BabyStage.ADOLESCENT:
            assert maturation >= 50.0, "Adolescent stage should have maturation greater than or equal to 50%"
        else:
            raise ValueError(f"Unexpected baby stage: {stage}")
    