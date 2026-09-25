"""Stepper component (real Beer CSS stepper idiom).

Renders the canonical Beer CSS stepper: a ``<nav>`` of ``button.circle.small`` step markers with
``<hr class="max">`` connectors. Completed steps (< current) show a ``done`` icon; the current
step shows its number; future steps (> current) are ``disabled``.
"""

from __future__ import annotations

from typing import Any

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class Stepper(Component):
    """A Material stepper. ``steps`` are labels; ``current`` is the active step index (0-based)."""

    def __init__(self, steps: list[str], *, current: int = 0) -> None:
        self.steps = steps
        self.current = current

    def render(self) -> Raw:
        children: list[Any] = []
        for i, label in enumerate(self.steps):
            if i > 0:
                children.append(tag("hr", class_="max"))
            if i < self.current:  # completed
                marker = tag("button", tag("i", "done"), class_="circle small")
            elif i == self.current:  # current
                marker = tag("button", str(i + 1), class_="circle small")
            else:  # future
                marker = tag("button", str(i + 1), class_="circle small", disabled=True)
            children.append(marker)
            children.append(tag("div", label, class_="mim-step-label"))
        return tag("nav", *children)
