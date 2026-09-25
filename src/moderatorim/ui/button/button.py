"""Button component (Beer CSS)."""

from __future__ import annotations

from typing import Any, Literal

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag

Variant = Literal["primary", "secondary", "destructive", "outline", "text"]
_VARIANTS = {
    "primary": "",
    "secondary": "secondary",
    "destructive": "error",
    "outline": "border",
    "text": "transparent",  # Beer CSS text button — no fill, no border
}


class Button(Component):
    """A Material button. Optional leading ``icon`` (Material Symbol). Extra kwargs → attributes
    (e.g. ``hx_post=...``); a caller-supplied ``class_`` is merged, not overwritten."""

    def __init__(
        self,
        label: str = "",
        *,
        icon: str = "",
        icon_trailing: bool = False,
        variant: Variant = "primary",
        type: str = "button",
        **extra: Any,
    ) -> None:
        self.label = label
        self.icon = icon
        self.icon_trailing = icon_trailing
        self.variant = variant
        self.type = type
        self.extra = extra

    def render(self) -> Raw:
        cls = f"button {_VARIANTS[self.variant]}".strip()
        extra = dict(self.extra)
        extra_cls = extra.pop("class_", "")
        if extra_cls:
            cls = f"{cls} {extra_cls}".strip()
        icon_el = tag("i", self.icon) if self.icon else None
        label_el = tag("span", self.label) if self.label else None
        children: list[Any] = []
        if self.icon_trailing:
            # label first, icon after (e.g. "Continue →")
            children = [c for c in (label_el, icon_el) if c is not None]
        else:
            children = [c for c in (icon_el, label_el) if c is not None]
        return tag("button", *children, type=self.type, class_=cls, **extra)
