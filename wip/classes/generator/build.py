"""Writes the generated blueprint modules under ``src/arkparse/classes``.

Run from this directory::

    python build.py

Modules listed in ``spec.MODULES`` are written whole. Modules listed in
``spec.EXTENSIONS`` already exist and are hand-curated: their blueprints are
appended straight into the classes that are already there (new stone structures
join ``class Stone``), and only genuinely new groups become new sibling classes.
Blueprints already written down anywhere in the package are skipped, so a second
run changes nothing.
"""

from pathlib import Path

import grouping
import patch
from categorize import group_all
from emit import render_group, render_module
from grouping import strip_markers
from naming import snake, leaf_of
from sources import load
from spec import MODULES, EXTENSIONS, RENAMES

CLASSES_DIR = Path(__file__).resolve().parents[3] / "src" / "arkparse" / "classes"


def _safe(name):
    return "bps" if name == "all_bps" else name


def _groups_for(entry, buckets, skip=()):
    """Resolve one spec entry into ``[(GroupName, [(attr, path)...]), ...]``."""
    if entry.get("split_by_category"):
        out = []
        for category in entry["categories"]:
            paths = [p for p in buckets.get(category, []) if p not in skip]
            if paths:
                noise = entry.get("noise", ())
                out.append((entry["category_classes"][category],
                            [(_safe(snake(strip_markers(leaf_of(p), noise))), p) for p in paths]))
        return out

    paths = [p for category in entry["categories"] for p in buckets.get(category, [])
             if p not in skip]
    groups = grouping.apply(paths, entry.get("rules", []),
                            fallback=entry.get("fallback", "Misc"),
                            attr=entry.get("attr"), renames=RENAMES,
                            noise=entry.get("noise", ()),
                            keep_markers=entry.get("keep_markers", False))
    return [(name, [(_safe(a), p) for a, p in entries]) for name, entries in groups]


def _write_module(entry, buckets):
    groups = _groups_for(entry, buckets)
    rendered = [(name, entries, None) for name, entries in groups]
    members = [(snake(name), name) for name, _ in groups]
    text = render_module(entry["header"], rendered, (entry["aggregate"], members, None))
    (CLASSES_DIR / f"{entry['module']}.py").write_text(text, encoding="utf-8")
    return sum(len(e) for _, e in groups), []


def _extend_module(entry, buckets):
    path = CLASSES_DIR / f"{entry['module']}.py"
    source = path.read_text(encoding="utf-8")

    # Never write a blueprint down twice: the dumps list everything a save
    # contains, including entries this module already spells out.
    known = patch.blueprint_paths(source)
    groups = _groups_for(entry, buckets, skip=known)

    existing = set(entry["existing"])
    added, fresh = 0, []
    for name, entries in groups:
        if not entries:
            continue
        if name in existing:
            source = patch.append_to_class(source, name, entries)
        else:
            source = patch.insert_class(source, entry["aggregate"],
                                        render_group(name, entries, None))
            fresh.append((snake(name), name))
        added += len(entries)

    if fresh:
        source = patch.register(source, entry["aggregate"], fresh)
    path.write_text(source, encoding="utf-8")
    return added, [name for _, name in fresh]


def build():
    buckets = group_all(load("all_classes"))
    report = []
    for entry in MODULES:
        count, fresh = _write_module(entry, buckets)
        report.append((entry["module"] + ".py", count, fresh))
    for entry in EXTENSIONS:
        count, fresh = _extend_module(entry, buckets)
        report.append((entry["module"] + ".py", count, fresh))

    for name, count, fresh in report:
        note = "  new classes: " + ", ".join(fresh) if fresh else ""
        print(f"{name:26s} {count:5d} blueprints{note}")
    print(f"{'TOTAL':26s} {sum(c for _, c, _ in report):5d}")


if __name__ == "__main__":
    build()
