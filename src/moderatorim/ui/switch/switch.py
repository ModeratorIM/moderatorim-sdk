"""Switch component (Beer CSS toggle) — for BOOLEAN columns."""

from __future__ import annotations

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class Switch(Component):
    """A Beer CSS switch (toggle) for a boolean value."""

    def __init__(
        self, name: str, *, label: str = "", checked: bool = False, disabled: bool = False
    ) -> None:
        self.name = name
        self.label = label
        self.checked = checked
        self.disabled = disabled

    def render(self) -> Raw:
        box = tag(
            "input",
            type="checkbox",
            name=self.name,
            id=self.name,
            checked=self.checked,
            disabled=self.disabled,
        )
        label_text = tag("span", self.label) if self.label else ""
        return tag(
            "label",
            tag("nav", tag("label", box, tag("span"), class_="switch"), label_text),
            class_="field middle-align",
        )
