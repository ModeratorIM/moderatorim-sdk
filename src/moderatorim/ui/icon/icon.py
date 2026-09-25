"""Icon component (Beer CSS / Material Symbols)."""

from __future__ import annotations

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class Icon(Component):
    """A Material Symbols icon, rendered as ``<i>name</i>``."""

    def __init__(self, name: str) -> None:
        self.name = name

    def render(self) -> Raw:
        return tag("i", self.name)
