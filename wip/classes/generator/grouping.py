"""Turns a flat list of blueprint paths into the named groups a module exposes.

A group rule is ``(ClassName, (marker, ...))``: a path joins the first group one
of whose markers appears in its class name. The markers are then stripped from
the attribute name, so ``PrimalItemSkin_ChibiDino_Direwolf`` becomes
``Chibis.direwolf`` rather than ``Chibis.chibi_dino_direwolf``.

Anything no rule claims goes to the module's fallback class, so grouping never
falls back on which map or DLC a blueprint shipped with.
"""

import re

from naming import leaf_of, snake, strip_noise

# What is left over once the prefixes and markers are gone is sometimes just a
# number or a bare asset suffix; those make useless attribute names.
UNUSABLE = {"bp", "sm", "c", "new", "base"}


def strip_markers(leaf: str, markers) -> str:
    """Remove the group markers from a leaf so the attribute reads cleanly.

    Falls back to the whole class name (minus the generic ``PrimalItem``) when
    stripping would leave nothing meaningful behind, so ``PrimalItemArtifactAB_2``
    becomes ``artifact_ab_2`` rather than ``_2``.
    """
    name = strip_noise(leaf)
    for marker in markers:
        token = marker.strip("_")
        name = re.sub(rf"(?:^|_){re.escape(token)}(?=_|$)", "_", name)
    name = name.strip("_")
    candidate = snake(name) if name else ""
    if not candidate or not any(c.isalpha() for c in candidate) or candidate in UNUSABLE:
        return re.sub(r"^PrimalItem", "", leaf)
    return name


def apply(paths, rules, fallback="Misc", attr=None, renames=None):
    """Return ``[(GroupName, [(attr, path), ...]), ...]`` in rule order.

    ``attr`` optionally overrides how an attribute name is derived from a leaf,
    for families whose names do not follow the usual ``<kind>_<what>`` shape.
    """
    buckets, order = {}, []
    for name, _ in rules:
        if name not in order:
            order.append(name)
    if fallback not in order:
        order.append(fallback)

    for path in paths:
        leaf = leaf_of(path)
        for name, markers in rules:
            if any(m in leaf for m in markers):
                derived = attr(leaf) if attr else snake(strip_markers(leaf, markers))
                break
        else:
            name = fallback
            derived = attr(leaf) if attr else snake(strip_noise(leaf))
        buckets.setdefault(name, []).append(((renames or {}).get(leaf, derived), path))

    return [(name, buckets[name]) for name in order if name in buckets]
