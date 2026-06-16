"""
Snapshot helpers for the testbench.

The first time a metric is recorded it is written to a JSON snapshot file keyed
by the save's identity (map name + file size). On later runs the same metric is
compared against the stored value so regressions in parsing show up as failures.

Set the env var ``TESTBENCH_UPDATE_SNAPSHOT=1`` (or run pytest with
``--update-snapshot``) to overwrite stored values with the current run.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"


class Snapshot:
    """Loads/stores a per-save snapshot and asserts metrics against it."""

    def __init__(self, save_key: str, update: bool = False):
        self.save_key = save_key
        self.update = update or os.environ.get("TESTBENCH_UPDATE_SNAPSHOT") == "1"
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        self.path = SNAPSHOT_DIR / f"{save_key}.json"
        self.data: Dict[str, Any] = {}
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
        self._dirty = False

    def check(self, metric: str, value: Any) -> None:
        """Assert ``value`` matches the snapshot for ``metric``.

        Records the value (without asserting) when no baseline exists yet or when
        running in update mode.
        """
        if self.update or metric not in self.data:
            self.data[metric] = value
            self._dirty = True
            print(f"  [snapshot] recorded {metric} = {value}")
            return

        expected = self.data[metric]
        assert value == expected, (
            f"Snapshot mismatch for '{metric}': expected {expected}, got {value}. "
            f"If this change is intended, re-run with --update-snapshot."
        )
        print(f"  [snapshot] {metric} = {value} (matches baseline)")

    def flush(self) -> None:
        if self._dirty:
            self.path.write_text(
                json.dumps(self.data, indent=2, sort_keys=True), encoding="utf-8"
            )
            self._dirty = False
