"""Heading component — a step/screen title: bolded, heading-sized ``<p>`` + optional subtitle.

Not an ``<h*>`` — the wizard and auth screens use styled paragraphs for their titles (so heading
size is a class decision, not a document-outline one). Shared by the setup wizard and auth
screens.
"""

from __future__ import annotations

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class Heading(Component):
    """A screen heading: bolded, heading-sized title + an optional muted subtitle."""

    def __init__(self, title: str, subtitle: str = "") -> None:
        self.title = title
        self.subtitle = subtitle

    def render(self) -> Raw:
        parts: list[object] = [tag("p", self.title, class_="mim-title bold large-text")]
        if self.subtitle:
            parts.append(tag("p", self.subtitle, class_="mim-subtitle small-text"))
        return tag("div", *parts, class_="mim-heading")
