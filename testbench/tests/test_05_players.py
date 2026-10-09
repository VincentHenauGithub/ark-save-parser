"""Player API: load players/tribes/pawns and snapshot the counts. Also checks
that every pawn-bearing player resolves an inventory, and that the loaded counts
agree with the .arkprofile/.arktribe files sitting next to the save."""
import pytest

from arkparse.api import PlayerApi
from arkparse.api.player_api import _TribeAndPlayerData
from arkparse.saves.save_connection import SaveConnection

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


def test_matches_files_on_disk(player_api: PlayerApi):
    """Guard against silently loading nothing.

    A save whose player/tribe data lives in .arkprofile/.arktribe files next to
    it must yield one player/tribe per file. Without this check a run that loads
    zero players still "passes" once a broken zero is baselined into the
    snapshot, which is exactly how a store-detection bug stayed hidden.
    """
    if player_api.from_store:
        pytest.skip("Player data comes from the in-save store; any files next "
                    "to the save are leftovers (see test_store_records_all_reachable)")

    save_dir = player_api.save.save_dir
    if save_dir is None:
        pytest.skip("Save has no directory on disk")

    # Counts kept in plain ints so a failure reports numbers, not path dumps.
    n_profile_files = len(list(save_dir.glob("*.arkprofile")))
    n_tribe_files = len(list(save_dir.glob("*.arktribe")))

    if n_profile_files == 0 and n_tribe_files == 0:
        pytest.skip(
            "No .arkprofile/.arktribe files next to the save "
            "(player data is expected to come from the in-save store)"
        )

    n_players = len(player_api.players)
    n_tribes = len(player_api.tribes)
    print(
        f"on disk: profiles={n_profile_files} tribes={n_tribe_files}; "
        f"loaded: players={n_players} tribes={n_tribes}"
    )

    assert n_players == n_profile_files, (
        f"{n_profile_files} .arkprofile file(s) next to the save but "
        f"{n_players} player(s) loaded (from_store={player_api.from_store})"
    )
    assert n_tribes == n_tribe_files, (
        f"{n_tribe_files} .arktribe file(s) next to the save but "
        f"{n_tribes} tribe(s) loaded (from_store={player_api.from_store})"
    )


def test_store_records_all_reachable(player_api: PlayerApi):
    """The in-save store path must not silently drop records either.

    Counterpart to test_matches_files_on_disk: when the data comes from the
    store there are no files to count against, so check the store's own
    bookkeeping instead.
    """
    if not player_api.from_store:
        pytest.skip("Player data comes from .arkprofile/.arktribe files")

    data = player_api.data
    n_player_ptrs = len(data.player_data_pointers)
    n_tribe_ptrs = len(data.tribe_data_pointers)
    n_players = len(player_api.players)
    n_tribes = len(player_api.tribes)
    print(
        f"store pointers: players={n_player_ptrs} tribes={n_tribe_ptrs}; "
        f"loaded: players={n_players} tribes={n_tribes}"
    )

    # The store is append-only, so a re-saved player leaves its older copies
    # behind; those collapse on player id and are counted as superseded.
    assert n_players + player_api.superseded_players == n_player_ptrs, (
        f"store located {n_player_ptrs} player record(s) but {n_players} "
        f"player(s) were loaded ({player_api.superseded_players} superseded)"
    )

    # The record boundary for the last player used to be computed as "up to the
    # next marker", which does not exist for the final one, so it was dropped.
    positions = data.data.find_byte_sequence(_TribeAndPlayerData.PLAYER_DATA_NAME)
    assert positions, "no player records found in the store"
    data.data.set_position(positions[-1] - 20)
    last_uuid = SaveConnection.byte_array_to_uuid(data.data.read_bytes(16))
    assert last_uuid in data.player_data_pointers, (
        "the last player record in the store was not picked up"
    )

    assert n_tribes > 0, "no tribes loaded from the store"
    assert n_tribes + player_api.superseded_tribes == n_tribe_ptrs, (
        f"{n_tribe_ptrs} tribe record(s) in the store but {n_tribes} loaded "
        f"({player_api.superseded_tribes} superseded)"
    )
