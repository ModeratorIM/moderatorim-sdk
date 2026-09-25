"""Validation result type (U2.2)."""

from __future__ import annotations

from dataclasses import dataclass

from moderatorim.sdk.validation.error import ValidationError


@dataclass(frozen=True, slots=True)
class Result:
    """The outcome of validating a form: ok, plus any errors grouped by field name."""

    errors: tuple[ValidationError, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors

    def by_field(self) -> dict[str, list[str]]:
        """Errors grouped as ``{field_name: [messages]}`` — convenient for rendering."""
        grouped: dict[str, list[str]] = {}
        for e in self.errors:
            grouped.setdefault(e.field, []).append(e.message)
        return grouped

    def first(self, field_name: str) -> str | None:
        """The first error message for a field, or None."""
        return next((e.message for e in self.errors if e.field == field_name), None)


# Convenience empty result.
OK = Result()
