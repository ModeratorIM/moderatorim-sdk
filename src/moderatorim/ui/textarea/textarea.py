"""Textarea component (Beer CSS labelled textarea) — for TEXTAREA columns."""

from __future__ import annotations

from typing import Any

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class Textarea(Component):
    """A Beer CSS labelled textarea for long/multi-line text."""

    def __init__(
        self,
        name: str,
        *,
        label: str = "",
        value: str = "",
        required: bool = False,
        disabled: bool = False,
        rows: int = 4,
        **extra: Any,
    ) -> None:
        self.name = name
        self.label = label
        self.value = value
        self.required = required
        self.disabled = disabled
        self.rows = rows
        self.extra = extra

    def render(self) -> Raw:
        area = tag(
            "textarea",
            self.value,
            name=self.name,
            id=self.name,
            required=self.required,
            disabled=self.disabled,
            rows=str(self.rows),
            **self.extra,
        )
        classes = ["field", "textarea", "border"]
        children: list[Any] = [area]
        if self.label:
            classes.insert(1, "label")
            children.append(tag("label", self.label, **{"for": self.name}))
        return tag("div", *children, class_=" ".join(classes))
