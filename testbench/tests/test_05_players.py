"""Player API: load players/tribes/pawns and snapshot the counts. Also checks
that every pawn-bearing player resolves an inventory."""
import pytest

from arkparse.api import PlayerApi

from snapshot import Snapshot


@pytest.fixture(scope="module")
def player_api(save) -> PlayerApi:
    return PlayerApi(save)


def test_loads(player_api: PlayerApi, snapshot: Snapshot):
    assert player_api.save is not None
    print(
        f"players={len(player_api.players)} "
        f"tribes={len(player_api.tribes)} pawns={len(player_api.pawns)}"
    )
    snapshot.check("players", len(player_api.players))
    snapshot.check("tribes", len(player_api.tribes))
    snapshot.check("pawns", len(player_api.pawns))


def test_pawn_inventories(player_api: PlayerApi):
    """Any player that has a pawn must resolve a (non-None) inventory."""
    checked = 0
    for player in player_api.players:
        if player_api.get_player_pawn(player) is not None:
            inv = player_api.get_player_inventory(player)
            assert inv is not None, (
                f"Player {player.name} has a pawn but no inventory"
            )
            checked += 1
    print(f"Verified inventories for {checked} pawn-bearing players")
