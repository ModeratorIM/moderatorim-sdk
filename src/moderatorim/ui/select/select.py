"""Select component (Beer CSS labelled select)."""

from __future__ import annotations

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class Select(Component):
    """A Beer CSS labelled select. ``options`` are (value, label) pairs."""

    def __init__(
        self, name: str, options: list[tuple[str, str]], *, label: str = "", value: str = ""
    ) -> None:
        self.name = name
        self.options = options
        self.label = label
        self.value = value

    def render(self) -> Raw:
        opts = [
            tag("option", opt_label, value=opt_value, selected=(opt_value == self.value))
            for opt_value, opt_label in self.options
        ]
        select = tag("select", *opts, name=self.name, id=self.name)
        if not self.label:
            return tag("div", select, class_="field suffix border")
        label_el = tag("label", self.label, **{"for": self.name})
        return tag("div", select, label_el, class_="field label suffix border")
