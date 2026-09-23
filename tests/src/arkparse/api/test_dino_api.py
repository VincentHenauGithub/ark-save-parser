
import json
import pytest
from pathlib import Path
from arkparse.api.dino_api import DinoApi
from arkparse import AsaSave
from arkparse.object_model.dinos import TamedDino, BabyStage
from arkparse.enums import ArkMap, ArkDinoTrait
from arkparse.parsing.game_object_reader_configuration import GameObjectReaderConfiguration

NR_DINOS = 34471
NR_TAMED = 2949
NR_WILD = 31522
NR_IN_CRYO = 2200
NR_WILD_BABIES = 2747
NR_TAMED_BABIES = 40
NR_BABIES = NR_WILD_BABIES + NR_TAMED_BABIES
NR_BABIES_IN_CRYO = 40

def dinos_per_map():
    """ Fixture to provide the expected number of dinos for each map. """
    return {
        ArkMap.RAGNAROK: NR_DINOS,
        ArkMap.ABERRATION: 22618,
        ArkMap.EXTINCTION: 20908,
        ArkMap.ASTRAEOS: 53679,
        ArkMap.SCORCHED_EARTH: 17175,
        ArkMap.THE_ISLAND: 31289,
        ArkMap.THE_CENTER: 45061,
        ArkMap.LOST_COLONY: 25672,
        ArkMap.VALGUERO: 38492,
        ArkMap.GENESIS: 23643,
    }

@pytest.fixture(scope="session")
def dino_api(ragnarok_save):
    """
    Fixture to provide a DinoApi instance for the Ragnarok save.
    """
    resource = DinoApi(ragnarok_save)
    yield resource

@pytest.fixture(scope="session")
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

def test_parse_dinos(map_save):
    """
    Test to parse the current map's save file and check the number of dinos.

    Maps without an explicit expectation fall back to "greater than zero".
    """
    map_name, save = map_save
    dinos = DinoApi(save).get_all()  # This will trigger the parsing of dinos
    print(f"Total dinos found in {map_name.name.title()}: {len(dinos)}")
    assert len(dinos) >= max(dinos_per_map().get(map_name, 0), 1), f"Unexpected number of dinos found for {map_name.name.title()}"

def test_get_all_dinos(dino_api: DinoApi):
    """
    Test to retrieve all tamed dinos from the Ragnarok save.
    """
    dinos = dino_api.get_all()
    assert isinstance(dinos, dict), "Expected a dictionary of dinos"
    print(f"Total dinos found: {len(dinos)}")
    assert len(dinos) >= NR_DINOS, f"Expectedat least {NR_DINOS} dinos, got {len(dinos)}"

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
    assert nr_tamed >= NR_TAMED, f"Expected at least {NR_TAMED} tamed dinos, got {nr_tamed}"
    assert nr_wild >= NR_WILD, f"Expected at least {NR_WILD} wild dinos, got {nr_wild}"
    assert in_cryopod_wild == 0, "There should be no wild dinos in cryopods"
    assert in_cryopod >= NR_IN_CRYO, f"Expected at least {NR_IN_CRYO} tamed dinos in cryopods, got {in_cryopod}"

def test_all_dinos_with_id_are_parsed(map_save):
    """
    For each map, check that every game object carrying a DinoID1 property is
    represented in the parsed dino set. Note: DinoID1 is not dino-exclusive
    (rafts, cars and other rideable actors carry it too), so mismatches are
    printed for inspection.
    """
    map_name, save = map_save
    dinos = DinoApi(save).get_all()

    print(f"[{map_name.name}] fetching containers with Dino ID properties")
    config = GameObjectReaderConfiguration()
    config.property_names = ["DinoID1"]
    with_id = save.get_game_objects(config)
    print(f"[{map_name.name}] Found {len(with_id)} objects with DinoID1 property")

    parsed_ids = {uuid.bytes for uuid in dinos.keys()}
    count = 0
    unparsed_bps = set()
    for uuid2, d in with_id.items():
        if uuid2.bytes not in parsed_ids:
            count += 1
            unparsed_bps.add(d.blueprint)
            print(f"[{map_name.name}] Object with DinoID1 not in parsed dinos: {d.blueprint} ({uuid2}) count={count}")

    # Compile the detected (unparsed) blueprints into a single alphabetical,
    # unique list next to this test file (merged across all maps)
    _dump_path = Path(__file__).parent / "unparsed_dinos_with_id.json"
    _existing = set(json.loads(_dump_path.read_text())) if _dump_path.exists() else set()
    _existing |= unparsed_bps
    _dump_path.write_text(json.dumps(sorted(_existing), indent=4))

    assert count == 0, f"[{map_name.name}] {count} objects with DinoID1 property not found in parsed dinos"

def test_gene_traits_are_parsed(dino_api: DinoApi):
    """
    Test that dino gene traits are parsed. Builds a map of trait type to the
    number of occurrences across all dinos. For now this only checks that at
    least one trait is parsed; counts per trait can be enforced later.
    """
    dinos = dino_api.get_all()

    trait_counts: dict[str, int] = {}
    for _, dino in dinos.items():
        for gene_trait in dino.gene_traits:
            trait_counts[str(gene_trait.trait)] = trait_counts.get(str(gene_trait.trait), 0) + 1

    print("Gene trait counts:")
    for trait, count in sorted(trait_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {trait}: {count}")

    total_traits = sum(trait_counts.values())
    print(f"Total gene traits parsed: {total_traits} across {len(trait_counts)} trait types")
    assert total_traits > 0, "Expected at least one gene trait to be parsed"

    assert total_traits >= 23584, f"Expected at least 23584 gene traits, got {total_traits}"
    assert len(trait_counts) >= 51, f"Expected at least 51 unique gene traits, got {len(trait_counts)}"

def test_gene_traits_json_export(dino_api: DinoApi):
    """
    Test that dino gene traits survive the JSON export path. Finds a dino that
    has gene traits, serializes it and verifies the traits are present in both
    the JSON object and the JSON string.
    """
    dinos = dino_api.get_all()

    dino_with_traits = next(
        (d for d in dinos.values() if d.gene_traits), None
    )
    assert dino_with_traits is not None, "Expected at least one dino with gene traits"

    json_obj = dino_with_traits.to_json_obj()
    assert "GeneTraits" in json_obj, "GeneTraits key missing from JSON object"
    assert len(json_obj["GeneTraits"]) == len(dino_with_traits.gene_traits), \
        "Number of exported gene traits does not match parsed gene traits"

    json_str = dino_with_traits.to_json_str()
    for gene_trait in dino_with_traits.gene_traits:
        assert str(gene_trait) in json_str, \
            f"Gene trait {gene_trait} missing from exported JSON string"

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
        
def test_get_tameable_dinos(dino_api: DinoApi):
    """
    Test to retrieve all tameable dinos from the Ragnarok save.
    """
    tameable_dinos = dino_api.get_all_wild_tamables()

    print(f"Total tameable dinos found: {len(tameable_dinos)}")
    

def _small_rag_save(base_save_path: Path) -> AsaSave:
    """A freshly opened copy of the small Ragnarok save.

    Selection tests have to parse the save themselves: the shared fixtures have
    already been through a full parse, and a warm cache would make a comparison
    between two selection strategies pass no matter what either one returned.
    """
    return AsaSave(base_save_path / "set_2" / "Ragnarok_WP" / "Ragnarok_WP.ark")


def test_cryopod_bp_detection():
    """Cryopods are still recognised by class path, so that check is pinned."""
    assert DinoApi.is_cryopod_bp(
        "/Game/Extinction/CoreBlueprints/Weapons/PrimalItem_WeaponEmptyCryopod."
        "PrimalItem_WeaponEmptyCryopod_C")
    assert DinoApi.is_cryopod_bp("/Cryopods/Cryopods/PrimalItem_WeaponEmptyCryopod_Mod."
                                 "PrimalItem_WeaponEmptyCryopod_Mod_C")
    assert DinoApi.is_cryopod_bp("/Game/Genesis2/CoreBlueprints/Items/ItemDinoball."
                                 "ItemDinoball_C")
    assert not DinoApi.is_cryopod_bp(
        "/Game/PrimalEarth/Dinos/Rex/Rex_Character_BP.Rex_Character_BP_C")
    assert not DinoApi.is_cryopod_bp(None)


def test_creature_selection_matches_class_path_filter(base_save_path: Path):
    """Selecting creatures by DinoID must find everything the class path found.

    The property scan is the robust one -- it does not have to recognise a mod's
    folder layout -- but it may not lose anything the old filter caught, and the
    cryopods and status components alongside it have to survive the switch too.
    """
    save = _small_rag_save(base_save_path)
    try:
        by_id = DinoApi(save).get_all_objects()
        by_name = DinoApi(save).get_all_objects(DinoApi._DEFAULT_CONFIG)
    finally:
        save.close()

    def creatures(objects):
        return {uuid for uuid, obj in objects.items()
                if any(p.name == "DinoID1" for p in obj.properties)}

    id_creatures, name_creatures = creatures(by_id), creatures(by_name)
    print(f"creatures by DinoID={len(id_creatures)} by class path={len(name_creatures)}")
    assert id_creatures, "expected the small save to contain creatures"

    missed = name_creatures - id_creatures
    assert not missed, f"{len(missed)} creature(s) the DinoID scan does not find"
    assert len(by_id) == len(by_name), (
        f"selection changed size: {len(by_id)} vs {len(by_name)}")


def test_tamed_selection_matches_class_path_filter(base_save_path: Path):
    """get_all_tamed must return the same dinos it did with the old config.

    Run against the full Ragnarok save: the small one has no tamed creatures at
    all, so it could only ever compare an empty set with an empty set.
    """
    old_config = GameObjectReaderConfiguration(
        blueprint_name_filter=lambda n: n is not None and DinoApi.is_applicable_bp(n),
        property_names=["TamedTimeStamp", "TamingTeamID", "CustomItemDatas"],
    )

    save = AsaSave(base_save_path / "set_1" / "Ragnarok_WP" / "Ragnarok_WP.ark")
    try:
        old = DinoApi(save).get_all(
            config=old_config, include_cryos=True, include_wild=False,
            include_tamed=True, include_babies=True)
        new = DinoApi(save).get_all_tamed(include_cryopodded=True)
    finally:
        save.close()

    print(f"tamed old={len(old)} new={len(new)}")
    assert len(new) == NR_TAMED, f"Expected {NR_TAMED} tamed dinos, got {len(new)}"
    assert set(new) == set(old), (
        f"only-old={len(set(old) - set(new))} only-new={len(set(new) - set(old))}")


def test_creature_config_falls_back_when_the_property_is_absent(base_save_path: Path):
    """A save whose name table lacks the property must not select everything.

    An unresolvable property name yields no byte pattern, which the reader reads
    as "no property filter" and would answer with the entire save. The small
    Ragnarok save has no tamed creatures and so no TamedTimeStamp name entry,
    which makes it the case to pin.
    """
    save = _small_rag_save(base_save_path)
    try:
        assert save.save_context.get_name_id("TamedTimeStamp") is None, (
            "this test needs a save whose name table lacks TamedTimeStamp")

        api = DinoApi(save)
        config = api._creature_reader_config(["TamedTimeStamp", "TamingTeamID"])
        assert config is DinoApi._DEFAULT_CONFIG, "expected the class-path fallback"

        # DinoID1 is present, so that one still takes the property scan.
        assert save.save_context.get_name_id("DinoID1") is not None
        by_id = api._creature_reader_config(["DinoID1", "DinoID2"])
        assert by_id is not DinoApi._DEFAULT_CONFIG
        assert by_id.property_names == ["DinoID1", "DinoID2"]
    finally:
        save.close()
