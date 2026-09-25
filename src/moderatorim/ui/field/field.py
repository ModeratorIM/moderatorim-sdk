"""Field component — wrap an arbitrary control with a label."""

from __future__ import annotations

from typing import Any

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class Field(Component):
    """A generic labelled field row wrapping an arbitrary ``control`` (component/Raw/str)."""

    def __init__(self, label: str, control: Any) -> None:
        self.label = label
        self.control = control

    def render(self) -> Raw:
        return tag("div", tag("label", self.label), self.control, class_="field label border")
