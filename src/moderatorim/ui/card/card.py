"""Card component (Beer CSS ``<article>``)."""

from __future__ import annotations

from typing import Any

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class Card(Component):
    """A Beer CSS card with an optional heading; composes any children/slots. A caller-supplied
    ``class_`` is merged with the base ``round``."""

    def __init__(self, *children: Any, title: str = "", **extra: Any) -> None:
        self.children = children
        self.title = title
        self.extra = extra

    def render(self) -> Raw:
        parts: list[Any] = []
        if self.title:
            parts.append(tag("h5", self.title))
        parts.extend(self.children)
        extra = dict(self.extra)
        cls = f"round {extra.pop('class_', '')}".strip()
        return tag("article", *parts, class_=cls, **extra)
