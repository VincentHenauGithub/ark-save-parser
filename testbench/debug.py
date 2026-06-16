"""
Capture objects that fail to parse, for offline debugging.

When registered via ``ArkSaveLogger.set_object_failure_handler`` (done in
conftest), every failed object is written to ``debug_dumps/<class>/<uuid>/``:

    object.bin              raw bytes of the object's byte buffer
    structured_print.txt    arkparse's structured property dump
    names.txt               the name table (find_names) for the object
    info.txt                uuid, class, error, position
    reparse.py              standalone script: reloads object.bin and re-parses
                            it with full parser logging so you can iterate on a
                            single object without touching the whole save

The reparse helper makes the loop tight: tweak the parser, run
``python debug_dumps/<class>/<uuid>/reparse.py``, read the logged trace, repeat.
"""
from __future__ import annotations

import io
import traceback
from pathlib import Path

DEBUG_DIR = Path(__file__).parent / "debug_dumps"

_REPARSE_TEMPLATE = '''\
"""Re-parse a single failed object for debugging.

Run:  python reparse.py

This reloads the object FROM THE SAVE (using its fully-populated name table /
save context) and re-parses just this one object with PARSER logging enabled, so
you see the exact step where parsing breaks. This is faithful to the original
full-save parse — edit the arkparse source, re-run, repeat.

If the save is no longer at the path below, point SAVE_PATH at it (or fall back
to the isolated object.bin in this folder — see the bottom of this file).
"""
import uuid as _uuid
from pathlib import Path

from arkparse import AsaSave
from arkparse.logging import ArkSaveLogger

HERE = Path(__file__).parent
OBJ_UUID = _uuid.UUID("{uuid}")
CLASS_NAME = "{class_name}"
SAVE_PATH = Path(r"{save_path}")

ArkSaveLogger.disable_all_logs()
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.PARSER, True)
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.ERROR, True)
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.WARNING, True)
ArkSaveLogger.allow_invalid_objects(False)
ArkSaveLogger.allow_invalid_mod_objects(False)

print(f"Re-parsing {{CLASS_NAME}}")
print(f"  uuid: {{OBJ_UUID}}")
print(f"  save: {{SAVE_PATH}}")

save = AsaSave(SAVE_PATH)
conn = save.save_connection
try:
    obj = conn.get_game_object_by_id(OBJ_UUID, reparse=True)
    print("Parsed OK:", obj)
except Exception as e:
    print("FAILED again:", e)
    raise

# --- Fallback: parse the isolated bytes only (no save context). Less faithful;
# name references may not resolve. Uncomment if the save is unavailable.
# from arkparse.parsing.ark_binary_parser import ArkBinaryParser
# from arkparse.object_model.ark_game_object import ArkGameObject
# data = (HERE / "object.bin").read_bytes()
# ArkGameObject(OBJ_UUID, CLASS_NAME, ArkBinaryParser(data))
'''


class FailedObjectDumper:
    """Stateful handler registered with ArkSaveLogger; dedupes by uuid."""

    def __init__(self, root: Path = DEBUG_DIR, save_path: Path | None = None):
        self.root = root
        self.save_path = save_path
        self.seen: set[str] = set()
        self.dumped: list[Path] = []

    def __call__(self, obj_uuid, class_name, byte_buffer, error) -> None:
        key = str(obj_uuid)
        if key in self.seen:
            return
        self.seen.add(key)

        safe_class = _safe_name(class_name)
        out = self.root / safe_class / key
        out.mkdir(parents=True, exist_ok=True)

        # 1. raw binary
        raw = getattr(byte_buffer, "byte_buffer", None)
        if raw is not None:
            (out / "object.bin").write_bytes(raw)

        # 2. structured property dump (write to our own handle, not the default)
        try:
            buf = io.BytesIO()
            byte_buffer.structured_print(to_file=buf, to_default_file=False)
            (out / "structured_print.txt").write_bytes(buf.getvalue())
        except Exception as e:
            (out / "structured_print.txt").write_text(
                f"structured_print failed: {e}\n", encoding="utf-8"
            )

        # 3. name table (positional, for eyeballing the binary)
        try:
            names = byte_buffer.find_names(no_print=True)
            lines = [f"{pos}: {name}" for pos, name in sorted(names.items())]
            (out / "names.txt").write_text("\n".join(lines), encoding="utf-8")
        except Exception as e:
            (out / "names.txt").write_text(f"find_names failed: {e}\n", encoding="utf-8")

        # 3b. the save's global name table (id -> name). The parser resolves name
        # references against this, so the reparse script needs it to reproduce the
        # *real* failure rather than a context-less mis-read.
        try:
            ctx = getattr(byte_buffer, "save_context", None)
            ctx_names = getattr(ctx, "names", None) if ctx is not None else None
            if ctx_names:
                import json
                # JSON keys must be strings; reparse.py converts them back to int.
                (out / "name_table.json").write_text(
                    json.dumps({str(k): v for k, v in ctx_names.items()}, indent=2),
                    encoding="utf-8",
                )
        except Exception as e:
            (out / "name_table.json").write_text(
                f'{{"_error": "{e}"}}', encoding="utf-8"
            )

        # 4. info
        (out / "info.txt").write_text(
            f"uuid:  {obj_uuid}\n"
            f"class: {class_name}\n"
            f"error: {error}\n"
            f"size:  {len(raw) if raw is not None else 'unknown'} bytes\n\n"
            f"{''.join(traceback.format_exception_only(type(error), error))}",
            encoding="utf-8",
        )

        # 5. reparse script (reloads from the save for a faithful re-parse)
        (out / "reparse.py").write_text(
            _REPARSE_TEMPLATE.format(
                uuid=obj_uuid,
                class_name=class_name,
                save_path=self.save_path or "SET_ME",
            ),
            encoding="utf-8",
        )

        self.dumped.append(out)
        print(f"  [debug] dumped failed object -> {out}")


def _safe_name(class_name: str) -> str:
    # /AwesomeAdminTools/.../BP_X.BP_X_C  ->  BP_X.BP_X_C  ->  filesystem-safe
    leaf = class_name.rstrip("/").split("/")[-1]
    return "".join(c if (c.isalnum() or c in "._-") else "_" for c in leaf) or "unknown"
