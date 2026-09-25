"""Safe HTML primitives.

Every component builds its markup through :func:`tag`, which escapes attribute values and
(unless explicitly given raw children) text content. This makes the component library
injection-safe by construction: a value rendered into an attribute or as text cannot break out
into markup. Raw (already-safe) HTML is passed as :class:`Raw`.
"""

from __future__ import annotations

import html
from typing import Any

# Void elements have no closing tag.
_VOID = {"input", "br", "hr", "img", "meta", "link"}


class Raw(str):
    """A string that is already safe HTML and must not be re-escaped (e.g. composed children)."""


def esc(value: Any) -> str:
    """HTML-escape ``value`` for safe text/attribute rendering.

    :class:`Raw` passes through unchanged. Any object implementing the ``__html__`` protocol
    (e.g. a :class:`~moderatorim.ui.component.Component`) is rendered via that method and
    treated as already-safe — this is what lets components compose as children without importing
    each other. Everything else is HTML-escaped.
    """
    if isinstance(value, Raw):
        return str(value)
    html_method = getattr(value, "__html__", None)
    if callable(html_method):
        return str(html_method())
    return html.escape(str(value), quote=True)


def attrs(mapping: dict[str, Any]) -> str:
    """Render an attribute mapping. ``True`` → bare boolean attr; ``False``/``None`` → omitted.

    Key normalization: a SINGLE trailing underscore is stripped first (the Python
    keyword-avoidance idiom, so ``class_`` → ``class`` and ``for_`` → ``for``); remaining
    underscores then become hyphens (so ``hx_post`` → ``hx-post``).
    """
    parts: list[str] = []
    for key, value in mapping.items():
        if value is None or value is False:
            continue
        name = key[:-1] if key.endswith("_") else key
        name = name.replace("_", "-")
        if value is True:
            parts.append(name)
        else:
            parts.append(f'{name}="{esc(value)}"')
    return (" " + " ".join(parts)) if parts else ""


def tag(_name: str, /, *children: Any, **attributes: Any) -> Raw:
    """Build an element. Children are escaped unless they are :class:`Raw`. Void elements
    (input/br/…) render self-closing and ignore children.

    The element name is positional-only (``_name``, before ``/``) so an HTML attribute called
    ``name`` can be passed as a keyword without colliding with this parameter.
    """
    open_tag = f"<{_name}{attrs(attributes)}>"
    if _name in _VOID:
        return Raw(open_tag)
    inner = "".join(esc(c) for c in children)
    return Raw(f"{open_tag}{inner}</{_name}>")
