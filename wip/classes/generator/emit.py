"""Renders grouped blueprint paths into the module shape used by arkparse.classes."""

from naming import resolve_names

WRAP = 110


def _wrap_list(names, indent="    "):
    """Render ``all_bps = [a, b, c]`` wrapped at a readable width."""
    lines, current = [], ""
    for i, name in enumerate(names):
        piece = name + ("," if i < len(names) - 1 else "")
        candidate = f"{current} {piece}".strip()
        if current and len(indent) + len("all_bps = [") + len(candidate) > WRAP:
            lines.append(current)
            current = piece
        else:
            current = candidate
    if current:
        lines.append(current)
    if len(lines) == 1:
        return f"{indent}all_bps = [{lines[0]}]"
    pad = indent + " " * len("all_bps = [")
    body = f"\n{pad}".join(lines)
    return f"{indent}all_bps = [{body}]"


def render_group(class_name, entries, docstring=None):
    """One leaf class: ``class Azure:`` with its attributes and ``all_bps``."""
    names = resolve_names(entries)
    out = [f"class {class_name}:"]
    if docstring:
        out.append(f'    """{docstring}"""')
    for name, path in zip(names, (p for _, p in entries)):
        out.append(f'    {name}: str = "{path}"')
    out.append("")
    out.append(_wrap_list(names))
    return "\n".join(out)


def render_aggregate(class_name, members, docstring=None):
    """The roll-up class: instantiates every group and sums their ``all_bps``."""
    out = [f"class {class_name}:"]
    if docstring:
        out.append(f'    """{docstring}"""')
    for attr, group in members:
        out.append(f"    {attr}: {group} = {group}()")
    out.append("")
    sums = [f"{attr}.all_bps" for attr, _ in members]
    lines, current = [], ""
    for i, piece in enumerate(sums):
        piece = piece + (" +" if i < len(sums) - 1 else "")
        candidate = f"{current} {piece}".strip()
        if current and len(candidate) > WRAP - 20:
            lines.append(current + " \\")
            current = piece
        else:
            current = candidate
    lines.append(current)
    out.append("    all_bps = " + f"\n        ".join(lines))
    return "\n".join(out)


def render_module(header, groups, aggregate):
    """Full module text: header docstring, every group, then the aggregate."""
    parts = [f'"""{header}"""', ""]
    for class_name, entries, doc in groups:
        parts.append(render_group(class_name, entries, doc))
        parts.append("")
    agg_name, members, agg_doc = aggregate
    parts.append(render_aggregate(agg_name, members, agg_doc))
    parts.append("")
    return "\n".join(parts)
