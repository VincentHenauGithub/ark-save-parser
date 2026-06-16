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

from arkparse.parsing.ark_binary_parser import ArkBinaryParser

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

# Player/tribe archives (.arkprofile / .arktribe) are self-contained — their name
# table is inline — so they reload directly from object.bin via ArkArchive.
_REPARSE_TEMPLATE_ARCHIVE = '''\
"""Re-parse a failed player/tribe archive object for debugging.

Run:  python reparse.py

Archives carry their own names inline, so this reloads object.bin directly via
ArkArchive and re-parses with PARSER logging — faithful to the original parse.
Edit the arkparse source, re-run, repeat.

(Note: for pre-Unreal-5.5 "old" saves the dumped bytes may be offset-stripped;
this loop targets 5.5+ archives, the common case.)
"""
from pathlib import Path

from arkparse.logging import ArkSaveLogger
from arkparse.parsing.ark_archive import ArkArchive

HERE = Path(__file__).parent
CLASS_NAME = "{class_name}"
FROM_STORE = {from_store}

ArkSaveLogger.disable_all_logs()
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.PARSER, True)
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.ERROR, True)
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.WARNING, True)
ArkSaveLogger.allow_invalid_objects(False)
ArkSaveLogger.allow_invalid_mod_objects(False)

data = (HERE / "object.bin").read_bytes()
print(f"Re-parsing archive containing {{CLASS_NAME}} from {{len(data)}} bytes (from_store={{FROM_STORE}})...")
try:
    archive = ArkArchive(data, from_store=FROM_STORE)
    print("Parsed OK:", len(archive.objects), "objects in archive")
except Exception as e:
    print("FAILED again:", e)
    raise
'''


class FailedObjectDumper:
    """Stateful handler registered with ArkSaveLogger; dedupes by uuid."""

    def __init__(self, root: Path = DEBUG_DIR, save_path: Path | None = None):
        self.root = root
        self.save_path = save_path
        self.seen: set[str] = set()
        self.dumped: list[Path] = []

    def __call__(self, obj_uuid, class_name, byte_buffer, error,
                 kind: str = "game", reload_hint: dict | None = None) -> None:
        raw = getattr(byte_buffer, "byte_buffer", None)

        # Game objects key off their uuid; archives have no per-object uuid, so
        # key off a content hash (dedupes identical failures, separates distinct).
        if obj_uuid is not None:
            key = str(obj_uuid)
        else:
            import hashlib
            digest = hashlib.sha1(raw or b"").hexdigest()[:12]
            key = f"{kind}_{digest}"

        if key in self.seen:
            return
        self.seen.add(key)

        safe_class = _safe_name(class_name)
        out = self.root / safe_class / key
        out.mkdir(parents=True, exist_ok=True)

        # 1. raw binary
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
            f"kind:  {kind}\n"
            f"uuid:  {obj_uuid}\n"
            f"class: {class_name}\n"
            f"error: {error}\n"
            f"size:  {len(raw) if raw is not None else 'unknown'} bytes\n\n"
            f"{''.join(traceback.format_exception_only(type(error), error))}",
            encoding="utf-8",
        )

        # 5. reparse script — game objects reload from the save; archives reload
        # from their own (self-contained) bytes.
        if kind == "archive":
            from_store = bool((reload_hint or {}).get("from_store", True))
            reparse = _REPARSE_TEMPLATE_ARCHIVE.format(
                class_name=class_name, from_store=from_store
            )
        else:
            reparse = _REPARSE_TEMPLATE.format(
                uuid=obj_uuid,
                class_name=class_name,
                save_path=self.save_path or "SET_ME",
            )
        (out / "reparse.py").write_text(reparse, encoding="utf-8")

        self.dumped.append(out)
        print(f"  [debug] dumped failed object ({kind}) -> {out}")


def _safe_name(class_name: str) -> str:
    # /AwesomeAdminTools/.../BP_X.BP_X_C  ->  BP_X.BP_X_C  ->  filesystem-safe
    leaf = class_name.rstrip("/").split("/")[-1]
    return "".join(c if (c.isalnum() or c in "._-") else "_" for c in leaf) or "unknown"


# Where non-fatal struct mismatches are recorded.
STRUCT_MISMATCH_DIR = DEBUG_DIR / "_struct_mismatches"


class StructMismatchRecorder:
    """Records non-fatal struct size mismatches (a struct parsed as a property
    list that under-/over-read its declared data_size, after which the parser
    realigns). These don't fail the parse but mark structs arkparse can't fully
    read. Deduped by struct type; the first occurrence of each type dumps the
    struct's bytes + structured print, and a summary tallies all of them.
    """

    def __init__(self, root: Path = STRUCT_MISMATCH_DIR):
        self.root = root
        self.counts: dict[str, int] = {}
        self.deltas: dict[str, int] = {}

    def __call__(self, struct_type, data_size, start_position, end_position, byte_buffer) -> None:
        self.counts[struct_type] = self.counts.get(struct_type, 0) + 1
        # delta > 0 => under-read (parser stopped short); < 0 => over-read.
        self.deltas[struct_type] = (start_position + data_size) - end_position

        if self.counts[struct_type] == 1:  # full dump on first sighting of a type
            out = self.root / _safe_name(struct_type)
            out.mkdir(parents=True, exist_ok=True)

            raw = getattr(byte_buffer, "byte_buffer", None)
            if raw is not None:
                struct_bytes = raw[start_position:start_position + data_size]
                (out / "struct.bin").write_bytes(struct_bytes)
                # Structured print of just the struct region, with the same context.
                try:
                    ctx = getattr(byte_buffer, "save_context", None)
                    sub = ArkBinaryParser(struct_bytes, ctx) if ctx is not None else ArkBinaryParser(struct_bytes)
                    buf = io.BytesIO()
                    sub.structured_print(to_file=buf, to_default_file=False)
                    (out / "structured_print.txt").write_bytes(buf.getvalue())
                except Exception as e:
                    (out / "structured_print.txt").write_text(
                        f"structured_print failed: {e}\n", encoding="utf-8"
                    )

            (out / "info.txt").write_text(
                f"struct_type:   {struct_type}\n"
                f"data_size:     {data_size}\n"
                f"start_position:{start_position}\n"
                f"end_position:  {end_position}\n"
                f"delta (declared_end - actual): {(start_position + data_size) - end_position}\n",
                encoding="utf-8",
            )

    def flush(self) -> None:
        if not self.counts:
            return
        self.root.mkdir(parents=True, exist_ok=True)
        lines = ["struct_type\tcount\tdelta(bytes)"]
        for st in sorted(self.counts, key=lambda s: -self.counts[s]):
            lines.append(f"{st}\t{self.counts[st]}\t{self.deltas[st]}")
        (self.root / "summary.txt").write_text("\n".join(lines), encoding="utf-8")
        total = sum(self.counts.values())
        print(f"  [debug] recorded {total} struct mismatch(es) across "
              f"{len(self.counts)} type(s) -> {self.root}")
