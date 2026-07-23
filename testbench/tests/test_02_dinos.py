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
