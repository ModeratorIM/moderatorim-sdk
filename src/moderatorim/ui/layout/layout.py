"""Layout components (Beer CSS) — Row, Grid, Nav. One-liner atoms grouped in one folder."""

from __future__ import annotations

from typing import Any

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class _Container(Component):
    """Shared base for the container atoms: a wrapper element with a base class that merges any
    caller-supplied ``class_``."""

    _tag = "div"
    _base_cls = ""

    def __init__(self, *children: Any, **extra: Any) -> None:
        self.children = children
        self.extra = extra

    def render(self) -> Raw:
        extra = dict(self.extra)
        cls = f"{self._base_cls} {extra.pop('class_', '')}".strip()
        attrs = {**extra, "class_": cls} if cls else extra
        return tag(self._tag, *self.children, **attrs)


class Row(_Container):
    """A horizontal flex row (Beer CSS ``row``)."""

    _base_cls = "row"


class Grid(_Container):
    """A responsive grid (Beer CSS ``grid``)."""

    _base_cls = "grid"


class Nav(_Container):
    """A nav container (``<nav>``)."""

    _tag = "nav"
    _base_cls = ""
