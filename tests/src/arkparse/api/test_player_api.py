import pytest
from arkparse.api import PlayerApi
from arkparse.player.ark_player import ArkPlayer
from arkparse.ark_tribe import ArkTribe
from arkparse.object_model.misc.inventory import Inventory
from arkparse.object_model.misc.dino_owner import DinoOwner
from arkparse.parsing.struct import ActorTransform

def get_test_player(player_api: PlayerApi | None) -> ArkPlayer:
    """
    Helper function to retrieve a specific player by name.
    """
    TEST_PLAYER_NAME = "Chokrobu"
    if player_api is None:
        return None
    return player_api.get_player_by_platform_name(TEST_PLAYER_NAME)

def get_test_tribe(player_api: PlayerApi | None) -> ArkTribe:
    TEST_TRIBE_NAME = "Imperium"
    for tribe in player_api.tribes:
        if tribe.name == TEST_TRIBE_NAME:
            return tribe
    return None

@pytest.fixture(scope="module")
def test_player(player_api: PlayerApi | None) -> ArkPlayer:
    """
    Fixture to retrieve a specific test player.
    """
    return get_test_player(player_api)

@pytest.fixture(scope="module")
def player_api(ragnarok_save) -> PlayerApi:
    """
    Helper function to retrieve the PlayerApi instance for a specific map.
    """
    return PlayerApi(ragnarok_save)

def test_player_api_initialization(player_api: PlayerApi | None):
    """
    Test the initialization of the PlayerApi.
    """
    assert player_api is not None, "PlayerApi should be initialized"
    assert isinstance(player_api, PlayerApi), f"Expected PlayerApi, got {type(player_api)}"
    assert player_api.save is not None, "PlayerApi save should not be None"
    
    assert len(player_api.players) == 100, f"Expected 100 players, got {len(player_api.players)}"
    assert len(player_api.tribes) == 74, f"Expected 74 tribes, got {len(player_api.tribes)}"
    assert len(player_api.pawns) == 67, f"Expected 67 pawns, got {len(player_api.pawns)}"

    test_player = get_test_player(player_api)
    assert test_player is not None, "Test player should be found"
    print(f"Test player: {test_player}")

    test_tribe = get_test_tribe(player_api)
    assert test_tribe is not None, "Test tribe should be found"
    print(f"Test tribe: {test_tribe}")

def test_player_pawn_retrieval(player_api: PlayerApi | None):
    """
    Test the retrieval of player pawns.
    """
    pawns = []
    for player in player_api.players:
        p = player_api.get_player_pawn(player)
        if p is not None:
            pawns.append(p)
    print(f"Total pawns retrieved: {len(pawns)}")
    assert len(pawns) == 59, f"Expected 59 pawns, got {len(pawns)}"

def test_pawn_inventories(player_api: PlayerApi | None):
    """
    Test the retrieval of pawn inventories.
    """
    for player in player_api.players:
        if player_api.get_player_pawn(player) is not None:
            inventory = player_api.get_player_inventory(player)
            assert inventory is not None, f"Inventory for player {player.name} should not be None as a pawn exists"

def test_get_player_with_highest_deaths(player_api: PlayerApi, test_player):
    p, val = player_api.get_player_with(stat=PlayerApi.Stat.DEATHS, stat_type=PlayerApi.StatType.HIGHEST)
    assert p is not None, "Expected a player object, got None"
    assert p.name == test_player.name, (
        f"Expected player {test_player.name}, got {p.name}"
    )
    assert int(val) == 678, (
        f"Expected 678 deaths for {test_player.name}, got {val}"
    )


def test_get_as_dino_owner(player_api: PlayerApi, test_player):
    o: DinoOwner = player_api.get_as_owner(PlayerApi.OwnerType.DINO, player_id=test_player.id_)
    assert o is not None, "Expected a DinoOwner object, got None"
    assert o.tamer_string == "Antartika", (
        f"Expected tamer tribe 'Antartika', got {o.tamer_string}"
    )


def test_get_deaths_for_player(player_api: PlayerApi, test_player):
    d: int = player_api.get_deaths(player=test_player.name)
    assert d == 678, (
        f"Expected 678 deaths for player {test_player.name}, got {d}"
    )


def test_get_player_inventory(player_api: PlayerApi, test_player):
    i: Inventory = player_api.get_player_inventory(test_player)
    assert i is not None, "Expected an Inventory object, got None"
    assert len(i.items) == 131, (
        f"Inventory should have 131 items, got {len(i.items)}"
    )


def test_get_player_pawn(player_api: PlayerApi, test_player):
    pawn = player_api.get_player_pawn(test_player)
    assert pawn is not None, (
        f"Expected a pawn for player {test_player.name}, got None"
    )
    assert hasattr(pawn, 'uuid'), (
        "Pawn object missing 'uuid' attribute"
    )


def test_get_tribe_of_player(player_api: PlayerApi, test_player):
    tribe: ArkTribe = player_api.get_tribe_of(test_player)
    assert tribe is not None, "Expected an ArkTribe object, got None"
    assert tribe.name == "Antartika", (
        f"Expected tribe 'Antartika', got {tribe.name}"
    )


def test_get_player_level(player_api: PlayerApi, test_player):
    lv = player_api.get_level(test_player.name)
    print(f"Player {test_player.name} level: {lv}")
    assert lv is not None, "Expected a level value, got None"
    assert lv == 156, (
        f"Expected level 156, got {lv}"
    )


def test_get_player_location_distance(player_api: PlayerApi, test_player):
    loc: ActorTransform = player_api.get_player_location(test_player)
    assert loc is not None, "Expected an ActorTransform object, got None"
    distance = loc.get_distance_to(ActorTransform())
    assert distance > 0, (  
        f"Expected non-zero distance, got {distance}"
    )


def test_get_player_xp(player_api: PlayerApi, test_player):
    xp = player_api.get_xp(test_player.name)
    print(f"Player {test_player.name} XP: {xp}")
    assert int(xp) > 383304000, (
        f"Expected >383304000 XP for player {test_player.name}, got {xp}"
    )

