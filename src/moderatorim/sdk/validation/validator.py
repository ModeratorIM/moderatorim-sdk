"""Running validators — the server-side enforcement path (U2.3, U2.5).

``validate_form`` is the security boundary: given the declared fields (name → validators) and the
POSTed data, it runs every validator server-side and returns a :class:`Result`. It is
**fail-closed**: a POSTed field that is not in the declared schema is an error, not silently
accepted.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from moderatorim.sdk.validation.error import ValidationError
from moderatorim.sdk.validation.result import Result
from moderatorim.sdk.validation.rules import Validator

# The declared field spec: field name → its validators.
FieldRules = Mapping[str, Sequence[Validator]]


def validate_field(value: str, validators: Sequence[Validator]) -> list[str]:
    """Return all error messages for ``value`` under ``validators`` (empty = valid)."""
    return [msg for v in validators if (msg := v.check(value)) is not None]


def validate_form(rules: FieldRules, data: Mapping[str, str]) -> Result:
    """Validate POSTed ``data`` against declared ``rules``. Fail-closed on unknown fields."""
    errors: list[ValidationError] = []

    # Fail-closed: reject any submitted field not in the declared schema.
    for submitted in data:
        if submitted not in rules:
            errors.append(ValidationError(submitted, "Unexpected field."))

    for name, validators in rules.items():
        value = data.get(name, "")
        for msg in validate_field(value, validators):
            errors.append(ValidationError(name, msg))

    return Result(errors=tuple(errors))
