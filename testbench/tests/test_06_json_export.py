"""JSON export: run JsonApi.export_all end-to-end and snapshot what it emits.

This is a whole-save integration smoke test - export_all drives every domain API
(equipment, players, dinos, structures, tribes, cluster data) and serializes the
results to JSON, so any regression in parsing or json serialization surfaces here.
"""
import json

import pytest

from arkparse import AsaSave
from arkparse.api.json_api import JsonApi

from snapshot import Snapshot


@pytest.fixture(scope="module")
def exports(save: AsaSave, tmp_path_factory: pytest.TempPathFactory):
    """Run export_all once into a temp folder and return the produced files."""
    out = tmp_path_factory.mktemp("json_exports")
    JsonApi(save).export_all(export_folder_path=out)
    files = sorted(out.glob("*.json"))
    print(f"export_all() wrote {len(files)} file(s) to {out}")
    for f in files:
        print(f"  - {f.name} ({f.stat().st_size} bytes)")
    return files


def test_export_all_produces_files(exports):
    assert exports, "export_all() produced no .json files"
    for f in exports:
        assert f.stat().st_size > 0, f"{f.name} is empty"


def test_export_all_is_valid_json(exports, snapshot: Snapshot):
    # Every file must parse, and the total number of exported records (entries in
    # list files) is a stable, regression-sensitive metric.
    total_records = 0
    for f in exports:
        data = json.loads(f.read_text(encoding="utf-8"))
        if isinstance(data, list):
            total_records += len(data)
    print(f"Total exported records across list files: {total_records}")
    snapshot.check("json_export_files", len(exports))
    snapshot.check("json_export_total_records", total_records)
