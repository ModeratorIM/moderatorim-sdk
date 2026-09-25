"""Input component (Beer CSS labelled field)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from moderatorim.sdk import Validator
from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class Input(Component):
    """A Beer CSS field: ``<div class="field label border"><input><label></div>``.

    ``validators`` (server-side rules) also contribute their HTML attributes to the input, so the
    same declaration drives browser-side hints and server-side enforcement.
    """

    def __init__(
        self,
        name: str,
        *,
        label: str = "",
        value: str = "",
        type: str = "text",
        placeholder: str = "",
        required: bool = False,
        icon: str = "",
        small: bool = False,
        validators: Sequence[Validator] = (),
        **extra: Any,
    ) -> None:
        self.name = name
        self.label = label
        self.value = value
        self.type = type
        self.placeholder = placeholder
        self.required = required
        self.icon = icon
        self.small = small
        self.validators = validators
        self.extra = extra

    def render(self) -> Raw:
        # Merge validator-derived HTML attrs (minlength, pattern, type=number min/max, …).
        attrs: dict[str, Any] = {}
        for v in self.validators:
            attrs.update(v.attrs())
        # Resolve the type/required that validators may override, then drop them from the splat.
        # NB: pop BEFORE combining — `self.required or attrs.pop(...)` would short-circuit and
        # leave 'required' in attrs when self.required is already True (a real bug we hit).
        input_type = attrs.pop("type", self.type)
        attr_required = bool(attrs.pop("required", False))
        required = self.required or attr_required
        field = tag(
            "input",
            name=self.name,
            id=self.name,
            type=input_type,
            value=self.value,
            placeholder=self.placeholder,
            required=required,
            **attrs,
            **self.extra,
        )
        # Beer CSS field wrapper. A leading icon adds the `prefix` class + an <i> before the input.
        children: list[Any] = []
        classes = ["field", "border"]
        if self.small:
            classes.append("small")  # Beer CSS small field modifier (shorter input)
        if self.icon:
            children.append(tag("i", self.icon))
            classes.insert(1, "prefix")
        children.append(field)
        if self.label:
            classes.insert(1, "label")
            children.append(tag("label", self.label, **{"for": self.name}))
        return tag("div", *children, class_=" ".join(classes))
