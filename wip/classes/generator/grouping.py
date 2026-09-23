"""Turns a flat list of blueprint paths into the named groups a module exposes.

A group rule is ``(ClassName, (marker, ...))``: a path joins the first group one
of whose markers appears in its class name. The markers are then stripped from
the attribute name, so ``PrimalItemSkin_ChibiDino_Direwolf`` becomes
``Chibis.direwolf`` rather than ``Chibis.chibi_dino_direwolf``.

Anything no rule claims goes to the module's fallback class, so grouping never
falls back on which map or DLC a blueprint shipped with.
"""

import re

from naming import leaf_of, snake, split_words, strip_noise

# What is left over once the prefixes and markers are gone is sometimes just a
# number or a bare asset suffix; those make useless attribute names.
UNUSABLE = {"bp", "sm", "c", "new", "base"}


def _remove_words(words, tokens):
    """Drop every occurrence of a contiguous token run from a word list."""
    if not tokens:
        return words
    out, i, n = [], 0, len(tokens)
    while i < len(words):
        if words[i:i + n] == tokens:
            i += n
        else:
            out.append(words[i])
            i += 1
    return out


def names_the_class(marker, class_name) -> bool:
    """Is the class already named after this marker?

    ``Adobe`` is, so ``SM_AdobeCeiling_BP`` should read ``ceiling``. ``Halloween``
    is not named after ``Coffin``, so ``StructureBP_Coffin_Upright`` keeps it and
    reads ``coffin_upright`` rather than a bare ``upright``.
    """
    cls = [w.lower() for w in split_words(class_name) if len(w) > 2]
    return any(c.startswith(m) or m.startswith(c)
               for m in (w.lower() for w in split_words(marker) if len(w) > 2)
               for c in cls)


def strip_markers(leaf: str, markers) -> str:
    """Remove the group markers from a leaf so the attribute reads cleanly.

    Matching happens on words rather than on the raw string, so a marker is
    found whether the asset spells it ``Ghost_Angler`` or ``GhostAngler``; a
    class named ``GhostCostumes`` should not hold ``ghost_angler``.

    Falls back to the whole class name (minus the generic ``PrimalItem``) when
    stripping would leave nothing meaningful behind, so ``PrimalItemArtifactAB_2``
    becomes ``artifact_ab_2`` rather than ``_2``.
    """
    base = [w.lower() for w in split_words(strip_noise(leaf))]
    words = base
    for marker in markers:
        words = _remove_words(words, [w.lower() for w in split_words(marker)])
    # Stripping every marker can leave nothing behind (``StructureBP_Coffin`` in
    # a class called Halloween). Keep the marker rather than the raw class name,
    # and only fall all the way back when even that says nothing.
    for candidate in ("_".join(words), "_".join(base),
                      snake(re.sub(r"^PrimalItem", "", leaf))):
        if (len(candidate) > 2 and any(c.isalpha() for c in candidate)
                and not candidate[0].isdigit() and candidate not in UNUSABLE):
            return candidate
    return snake(leaf)


def apply(paths, rules, fallback="Misc", attr=None, renames=None, noise=(),
          keep_markers=False):
    """Return ``[(GroupName, [(attr, path), ...]), ...]`` in rule order.

    ``attr`` optionally overrides how an attribute name is derived from a leaf,
    for families whose names do not follow the usual ``<kind>_<what>`` shape.
    ``noise`` lists tokens stripped from every name in the module, for the
    boilerplate a whole family carries (``Zombie_Character_BP_Bloated`` reads as
    ``zombie_bloated``). ``keep_markers`` leaves the group marker in the name,
    for modules where it is part of what the thing is called rather than a
    category label -- a zombie dino is still a zombie once it is in ``Zombies``.
    """
    noise = tuple(noise)
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
                strip = noise if keep_markers else noise + tuple(
                    m for m in markers if names_the_class(m, name))
                derived = attr(leaf) if attr else snake(strip_markers(leaf, strip))
                break
        else:
            name = fallback
            derived = attr(leaf) if attr else snake(strip_markers(leaf, noise))
        buckets.setdefault(name, []).append(((renames or {}).get(leaf, derived), path))

    return [(name, buckets[name]) for name in order if name in buckets]
