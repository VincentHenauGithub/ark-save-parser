"""In-place editing of the hand-written modules under ``src/arkparse/classes``.

New blueprints are appended straight into the class they belong to -- new stone
structures land in ``class Stone`` next to the ones that are already there --
rather than in a parallel set of classes. Blueprints already present anywhere in
the package are skipped, so re-running the generator is a no-op.
"""

import re

from naming import resolve_names

ATTR = re.compile(r'^(\s*)([A-Za-z_]\w*)\s*(?::\s*str\s*)?=\s*"(/[^"]*)"\s*$')
ASSIGN = re.compile(r"^(\s*)all_bps\s*=")


def blueprint_paths(text):
    """Every blueprint string already written down in a module."""
    return set(re.findall(r'"(/[^"]*_C)"', text))


def _class_bounds(lines, name):
    """Line range ``[start, end)`` of a class body, nested classes included."""
    for i, line in enumerate(lines):
        match = re.match(rf"^(\s*)class {re.escape(name)}\s*[:(]", line)
        if not match:
            continue
        indent = len(match.group(1))
        end = len(lines)
        for j in range(i + 1, len(lines)):
            stripped = lines[j].strip()
            if stripped and len(lines[j]) - len(lines[j].lstrip()) <= indent:
                end = j
                break
        return i, end
    raise KeyError(name)


def _assignment_span(lines, start, end):
    """Line range of the ``all_bps = ...`` statement inside a class body."""
    for i in range(start, end):
        if ASSIGN.match(lines[i]):
            j = i
            while True:
                chunk = "\n".join(lines[i:j + 1])
                balanced = chunk.count("[") == chunk.count("]")
                if balanced and not chunk.rstrip().endswith("\\"):
                    return i, j + 1
                j += 1
                if j >= end:
                    return i, end
    return None


def _style(lines, start, end):
    """Match the attribute style the class already uses."""
    for i in range(start, end):
        match = ATTR.match(lines[i])
        if match:
            return match.group(1), ": str = " if ": str" in lines[i] else " = "
    return "    ", ": str = "


def _names_in(lines, start, end):
    """Attribute names defined directly in a class body, in source order."""
    return [m.group(2) for m in (ATTR.match(lines[i]) for i in range(start, end)) if m]


def _render_list(names, indent):
    """Render ``all_bps = [...]`` wrapped the way the rest of the package does."""
    head = f"{indent}all_bps = ["
    rows, current = [], ""
    for i, name in enumerate(names):
        piece = name + ("," if i < len(names) - 1 else "")
        candidate = f"{current} {piece}".strip()
        if current and len(head) + len(candidate) > 110:
            rows.append(current)
            current = piece
        else:
            current = candidate
    rows.append(current)
    pad = " " * len(head)
    return [head + rows[0]] + [pad + row for row in rows[1:-1]] +            ([pad + rows[-1]] if len(rows) > 1 else [])


def _close(rows):
    rows[-1] = rows[-1] + "]"
    return rows


def append_to_class(text, class_name, entries):
    """Add ``entries`` (``[(attr, path), ...]``) to an existing class."""
    lines = text.split("\n")
    start, end = _class_bounds(lines, class_name)
    indent, sep = _style(lines, start, end)

    attrs = resolve_names(entries, taken=_names_in(lines, start, end))
    entries = list(zip(attrs, (path for _, path in entries)))
    new_lines = [f'{indent}{attr}{sep}"{path}"' for attr, path in entries]
    span = _assignment_span(lines, start, end)

    if span is None:
        names = _names_in(lines, start, end) + [a for a, _ in entries]
        insert_at = end
        while insert_at > start and not lines[insert_at - 1].strip():
            insert_at -= 1
        block = new_lines + [""] + _close(_render_list(names, indent))
        return "\n".join(lines[:insert_at] + block + lines[insert_at:])

    first, last = span
    names = _names_in(lines, start, end) + [a for a, _ in entries]
    rebuilt = _close(_render_list(names, ASSIGN.match(lines[first]).group(1)))
    return "\n".join(lines[:first] + new_lines + [""] + rebuilt + lines[last:])


def register(text, aggregate, members):
    """Add ``name: Cls = Cls()`` members to a roll-up class and to its sum."""
    lines = text.split("\n")
    start, end = _class_bounds(lines, aggregate)
    span = _assignment_span(lines, start, end)
    if span is None:
        raise KeyError(f"{aggregate} has no all_bps")
    first, last = span

    body = "\n".join(lines[start:end])
    fresh = [(attr, cls) for attr, cls in members if f"{attr}: {cls} = {cls}()" not in body]
    indent = re.match(r"^(\s*)", lines[first]).group(1)
    declarations = [f"{indent}{attr}: {cls} = {cls}()" for attr, cls in fresh]

    assignment = lines[first:last]
    additions = [f"{attr}.all_bps" for attr, _ in members
                 if f"{attr}.all_bps" not in "\n".join(assignment)]
    if additions:
        assignment[-1] = assignment[-1].rstrip() + " + \\"
        pad = indent + " " * 8
        wrapped, current = [], pad
        for piece in additions:
            candidate = f"{current} {piece} +".rstrip(" +") if current.strip() else pad + piece
            if len(candidate) > 110:
                wrapped.append(current.rstrip() + " + \\")
                current = pad + piece
            else:
                current = (current.rstrip() + " + " + piece) if current.strip() else pad + piece
        wrapped.append(current)
        assignment = assignment + wrapped

    head = lines[:first]
    while head and not head[-1].strip():
        head.pop()
    return "\n".join(head + declarations + [""] + assignment + lines[last:])


def insert_class(text, before, class_text):
    """Place a freshly generated class just above the module's roll-up class."""
    lines = text.split("\n")
    start, _ = _class_bounds(lines, before)
    while start > 0 and not lines[start - 1].strip():
        start -= 1
    block = class_text.split("\n") + [""]
    return "\n".join(lines[:start] + [""] + block + lines[start:])
