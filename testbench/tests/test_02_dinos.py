"""Dino API: parse all dinos and snapshot the wild/tamed/cryo/baby breakdown.
Also verifies type and baby-stage invariants that must hold for any save."""
from arkparse.parsing.game_object_reader_configuration import GameObjectReaderConfiguration
from arkparse.saves.asa_save import AsaSave
import pytest

from arkparse.api.dino_api import DinoApi
from arkparse.object_model.dinos import TamedDino, BabyStage

from snapshot import Snapshot


@pytest.fixture(scope="module")
def dino_api(save) -> DinoApi:
    return DinoApi(save)


def test_get_all(dino_api: DinoApi, snapshot: Snapshot):
    dinos = dino_api.get_all()
    assert isinstance(dinos, dict), "Expected a dict of dinos"
    print(f"Total dinos: {len(dinos)}")
    snapshot.check("dinos_total", len(dinos))


def test_breakdown(dino_api: DinoApi, snapshot: Snapshot, save):
    dinos = dino_api.get_all()
    tamed = wild = cryo_tamed = cryo_wild = 0
    for dino in dinos.values():
        if isinstance(dino, TamedDino):
            tamed += 1
            if dino.is_cryopodded:
                cryo_tamed += 1
        else:
            wild += 1
            if dino.is_cryopodded:
                cryo_wild += 1

    print("fetching containers with Dino ID properties")
    config = GameObjectReaderConfiguration()
    config.property_names = ["DinoID1"]
    save: AsaSave = save
    with_id = save.get_game_objects(config)
    print(f"Found {len(with_id)} dinos with DinoID1 property")

    count = 0
    for uuid2, d in with_id.items():
        found = False
        
        for uuid, dino in dinos.items():
            if uuid.bytes == uuid2.bytes:
                found = True
                break
        if not found:
            count += 1
            print(f"Dino not found in containers: {d.blueprint} ({uuid2}) count={count}")

    assert count == 0, f"{count} dinos with DinoID1 property not found in containers"


    print(f"tamed={tamed} wild={wild} cryo_tamed={cryo_tamed} cryo_wild={cryo_wild}")
    assert tamed + wild == len(dinos), "tamed + wild must equal total"
    assert cryo_wild == 0, "wild dinos should never be cryopodded"

    snapshot.check("dinos_tamed", tamed)
    snapshot.check("dinos_wild", wild)
    snapshot.check("dinos_cryopodded", cryo_tamed)


def test_wild_and_tamed_getters(dino_api: DinoApi):
    """The dedicated getters must agree with the manual breakdown."""
    wild = dino_api.get_all_wild()
    tamed = dino_api.get_all_tamed()
    assert isinstance(wild, dict) and isinstance(tamed, dict)
    print(f"get_all_wild()={len(wild)}  get_all_tamed()={len(tamed)}")
    for d in tamed.values():
        assert isinstance(d, TamedDino), f"get_all_tamed returned {type(d)}"


def test_babies(dino_api: DinoApi, snapshot: Snapshot):
    babies = dino_api.get_all_babies(
        include_tamed=True, include_cryopodded=True, include_wild=True
    )
    assert isinstance(babies, dict)
    print(f"Total babies: {len(babies)}")
    snapshot.check("dinos_babies", len(babies))

    for baby in babies.values():
        stage = baby.stage
        maturation = baby.percentage_matured
        if stage == BabyStage.BABY:
            assert maturation < 10.0, f"BABY stage maturation {maturation} >= 10%"
        elif stage == BabyStage.JUVENILE:
            assert 10.0 <= maturation < 50.0, f"JUVENILE maturation {maturation} out of range"
        elif stage == BabyStage.ADOLESCENT:
            assert maturation >= 50.0, f"ADOLESCENT maturation {maturation} < 50%"
        else:
            raise ValueError(f"Unexpected baby stage: {stage}")


def test_cryopod_bp_detection():
    """Cryopods are still recognised by class path, so that check is pinned."""
    assert DinoApi.is_cryopod_bp(
        "/Game/Extinction/CoreBlueprints/Weapons/PrimalItem_WeaponEmptyCryopod."
        "PrimalItem_WeaponEmptyCryopod_C")
    assert DinoApi.is_cryopod_bp("/Cryopods/Cryopods/PrimalItem_WeaponEmptyCryopod_Mod."
                                 "PrimalItem_WeaponEmptyCryopod_Mod_C")
    assert not DinoApi.is_cryopod_bp(
        "/Game/PrimalEarth/Dinos/Rex/Rex_Character_BP.Rex_Character_BP_C")
    assert not DinoApi.is_cryopod_bp(None)


def test_creature_selection_matches_class_path_filter(save_file):
    """Selecting creatures by DinoID must find what the class-path filter finds.

    The property scan is the robust one -- it does not need to recognise a mod's
    folder layout -- but it may not lose anything the old filter caught. Both
    runs open the save fresh: the session fixture has already parsed everything,
    and a shared parse cache would make the comparison meaningless.
    """
    by_id = AsaSave(save_file)
    by_name = AsaSave(save_file)

    id_objects = DinoApi(by_id).get_all_objects()
    name_objects = DinoApi(by_name).get_all_objects(DinoApi._DEFAULT_CONFIG)

    def creatures(objects):
        return {uuid for uuid, obj in objects.items()
                if any(p.name == "DinoID1" for p in obj.properties)}

    id_creatures, name_creatures = creatures(id_objects), creatures(name_objects)
    print(f"creatures by DinoID={len(id_creatures)} by class path={len(name_creatures)}")

    missed = name_creatures - id_creatures
    assert not missed, f"{len(missed)} creature(s) the DinoID scan does not find"

    # Cryopods and status components must survive the switch as well.
    assert len(id_objects) == len(name_objects), (
        f"selection changed size: {len(id_objects)} vs {len(name_objects)}")


def test_tamed_selection_matches_class_path_filter(save_file):
    """get_all_tamed must return the same dinos it did with the old config."""
    old_config = GameObjectReaderConfiguration(
        blueprint_name_filter=lambda n: n is not None and DinoApi.is_applicable_bp(n),
        property_names=["TamedTimeStamp", "TamingTeamID", "CustomItemDatas"],
    )
    old = DinoApi(AsaSave(save_file)).get_all(
        config=old_config, include_cryos=True, include_wild=False,
        include_tamed=True, include_babies=True)
    new = DinoApi(AsaSave(save_file)).get_all_tamed(include_cryopodded=True)

    print(f"tamed old={len(old)} new={len(new)}")
    assert set(new) == set(old), (
        f"only-old={len(set(old) - set(new))} only-new={len(set(new) - set(old))}")
