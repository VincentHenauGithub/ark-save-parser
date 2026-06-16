# Testbench

A standalone harness for running the full arkparse API suite against **one
arbitrary `.ark` save** that you drop in — no map-specific expected values
hardcoded.

## Usage

1. Put your save under `test_save/`. Either layout works:

   ```
   testbench/test_save/Ragnarok_WP/Ragnarok_WP.ark      # the whole save folder
   testbench/test_save/whatever.ark                     # just the .ark file
   ```

   The first `.ark` found recursively is used. `test_save/` is gitignored.

2. Run from this directory:

   ```bash
   cd testbench
   pytest
   ```

   First run **records** every metric to `snapshots/<map>_<size>.json`.
   Later runs **compare** against it, so parser regressions surface as failures.

## Snapshots

Counts (objects, dinos, structures, equipment, players, …) are stored per save,
keyed by map name + file size. To accept new values after an intentional change:

```bash
pytest --update-snapshot
# or
TESTBENCH_UPDATE_SNAPSHOT=1 pytest
```

Snapshots are gitignored by default; commit `snapshots/` if you want the
baseline tracked.

## Layout

| File | Purpose |
|------|---------|
| `conftest.py` | Autodetects the save, parses it once, wires snapshot fixtures |
| `snapshot.py` | Snapshot load / store / compare helper |
| `tests/test_01_parsing.py` | Load, faulty-object check, game time, GeneralApi |
| `tests/test_02_dinos.py` | DinoApi: totals, wild/tamed/cryo breakdown, babies |
| `tests/test_03_structures.py` | StructureApi totals |
| `tests/test_04_equipment.py` | EquipmentApi: armor/weapons/saddles/shields |
| `tests/test_05_players.py` | PlayerApi: players/tribes/pawns + inventories |

## Debugging a parse

To see full parser logs while investigating a problem save, edit the logging
block at the top of `conftest.py` (e.g. enable `DEBUG`), or run a single file:

```bash
pytest tests/test_02_dinos.py -k breakdown
```

The suite stops at the **first failure** (`-x` in `pytest.ini`) so the structured
parser output stays at the bottom of the run, easy to read.

## Failed-object debug dumps

Every object that fails to parse is captured under `debug_dumps/<class>/<uuid>/`
(cleared at the start of each run, gitignored):

| File | Contents |
|------|----------|
| `object.bin` | raw bytes of the object's byte buffer |
| `structured_print.txt` | arkparse's structured property dump (full context) |
| `names.txt` | positional name table for eyeballing the binary |
| `name_table.json` | the save's global name table (id → name) reference |
| `info.txt` | uuid, class, error, size |
| `reparse.py` | **standalone re-parse of just this object, from the save** |

To iterate on a single broken object:

```bash
python debug_dumps/<class>/<uuid>/reparse.py
```

It reloads that one object from the save with full PARSER logging and reproduces
the exact failure. Edit the arkparse parser, re-run, repeat — no need to re-parse
the whole save each time.

### Faulty-object policy

`conftest.py` sets two flags:

```python
ArkSaveLogger.allow_invalid_objects(False)       # /Game/ & /Script/ objects
ArkSaveLogger.allow_invalid_mod_objects(False)   # mod-namespace objects
```

`allow_invalid_mod_objects` is a separate flag (added for the testbench) so mod
blueprints — which the library used to silently skip — are also treated as hard
failures. Set either to `True` to let those objects be skipped instead.
