"""Build validators from a JSON ``validation`` block (U2.6).

Maps a config_schema field's ``validation`` dict (e.g. ``{"min_length": 3, "max_length": 80}``)
into concrete :mod:`rules` validators, so a form declared as data gets both the rendered HTML
attributes and server-side enforcement from the same source.
"""

from __future__ import annotations

from typing import Any

from moderatorim.sdk.validation.rules import (
    Email,
    Max,
    MaxLength,
    Min,
    MinLength,
    Pattern,
    Required,
    Validator,
)


def build_validators(spec: dict[str, Any]) -> list[Validator]:
    """Turn a field spec (with optional ``required`` + ``validation`` block) into validators."""
    validators: list[Validator] = []
    if spec.get("required"):
        validators.append(Required())
    v = spec.get("validation", {})
    if "min_length" in v:
        validators.append(MinLength(int(v["min_length"])))
    if "max_length" in v:
        validators.append(MaxLength(int(v["max_length"])))
    if "min" in v:
        validators.append(Min(float(v["min"])))
    if "max" in v:
        validators.append(Max(float(v["max"])))
    if "pattern" in v:
        validators.append(Pattern(str(v["pattern"])))
    if v.get("email") or spec.get("type") == "email":
        validators.append(Email())
    return validators
