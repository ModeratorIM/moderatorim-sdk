"""Pills component (Beer CSS chips) — for LISTREF columns (a list of references).

Renders each selected record as a removable chip, over hidden inputs carrying the selected ids.
The candidate picker (a select of allowable targets) is supplied by the caller/renderer, since its
options come from the referenced table (filtered by that table's ACL).
"""

from __future__ import annotations

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class Pills(Component):
    """Selected references shown as removable chips, backed by hidden ``name`` inputs.

    ``selected`` is a list of (id, label) pairs. Each chip carries the label + an ✕; the id rides in
    a hidden ``<input name=<name> value=<id>>`` so a form POST submits the full set. ``picker`` (an
    optional pre-rendered control, e.g. a Select of candidates) is appended for adding more.
    """

    def __init__(
        self,
        name: str,
        selected: list[tuple[str, str]],
        *,
        label: str = "",
        picker: Component | Raw | str = "",
        disabled: bool = False,
    ) -> None:
        self.name = name
        self.selected = selected
        self.label = label
        self.picker = picker
        self.disabled = disabled

    def render(self) -> Raw:
        chips = []
        for rid, rlabel in self.selected:
            children = [rlabel]
            if not self.disabled:
                children.append(tag("i", "close"))
            chips.append(
                tag(
                    "button",
                    tag("input", type="hidden", name=self.name, value=rid),
                    *children,
                    class_="chip",
                    type="button",
                    data_id=rid,
                )
            )
        parts: list[Component | Raw | str] = []
        if self.label:
            parts.append(tag("label", self.label))
        parts.append(tag("div", *chips, class_="row wrap"))
        if self.picker and not self.disabled:
            parts.append(self.picker)
        return tag("div", *parts, class_="field")
