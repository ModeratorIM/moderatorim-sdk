"""Validator primitives (U2.1).

Each :class:`Validator` knows BOTH how to (a) render itself as HTML input attributes (browser-side
UX) and (b) check a submitted value (server-side enforcement). One declaration, two uses — they
cannot drift. ``check`` returns an error message on failure, or ``None`` on pass.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class Validator(ABC):
    """A single field validation rule."""

    @abstractmethod
    def attrs(self) -> dict[str, Any]:
        """HTML input attributes expressing this rule (browser-side hint)."""
        ...

    @abstractmethod
    def check(self, value: str) -> str | None:
        """Return an error message if ``value`` violates this rule, else ``None`` (server-side)."""
        ...


@dataclass(frozen=True, slots=True)
class Required(Validator):
    message: str = "This field is required."

    def attrs(self) -> dict[str, Any]:
        return {"required": True}

    def check(self, value: str) -> str | None:
        return None if value.strip() else self.message


@dataclass(frozen=True, slots=True)
class MinLength(Validator):
    length: int
    message: str = ""

    def attrs(self) -> dict[str, Any]:
        return {"minlength": self.length}

    def check(self, value: str) -> str | None:
        if value and len(value) < self.length:
            return self.message or f"Must be at least {self.length} characters."
        return None


@dataclass(frozen=True, slots=True)
class MaxLength(Validator):
    length: int
    message: str = ""

    def attrs(self) -> dict[str, Any]:
        return {"maxlength": self.length}

    def check(self, value: str) -> str | None:
        if len(value) > self.length:
            return self.message or f"Must be at most {self.length} characters."
        return None


@dataclass(frozen=True, slots=True)
class Min(Validator):
    value: float
    message: str = ""

    def attrs(self) -> dict[str, Any]:
        return {"type": "number", "min": self.value}

    def check(self, value: str) -> str | None:
        if not value:
            return None
        try:
            n = float(value)
        except ValueError:
            return "Must be a number."
        return None if n >= self.value else (self.message or f"Must be ≥ {self.value}.")


@dataclass(frozen=True, slots=True)
class Max(Validator):
    value: float
    message: str = ""

    def attrs(self) -> dict[str, Any]:
        return {"type": "number", "max": self.value}

    def check(self, value: str) -> str | None:
        if not value:
            return None
        try:
            n = float(value)
        except ValueError:
            return "Must be a number."
        return None if n <= self.value else (self.message or f"Must be ≤ {self.value}.")


@dataclass(frozen=True, slots=True)
class Pattern(Validator):
    regex: str
    message: str = "Invalid format."

    def attrs(self) -> dict[str, Any]:
        return {"pattern": self.regex}

    def check(self, value: str) -> str | None:
        if not value:
            return None
        return None if re.fullmatch(self.regex, value) else self.message


@dataclass(frozen=True, slots=True)
class Email(Validator):
    message: str = "Enter a valid email address."
    _re: str = r"[^@\s]+@[^@\s]+\.[^@\s]+"

    def attrs(self) -> dict[str, Any]:
        return {"type": "email"}

    def check(self, value: str) -> str | None:
        if not value:
            return None
        return None if re.fullmatch(self._re, value) else self.message


@dataclass(frozen=True, slots=True)
class OneOf(Validator):
    choices: tuple[str, ...]
    message: str = ""

    def attrs(self) -> dict[str, Any]:
        return {}  # enforced by the <select> options; no extra input attr

    def check(self, value: str) -> str | None:
        if not value:
            return None
        return None if value in self.choices else (self.message or "Not an allowed value.")


@dataclass(frozen=True, slots=True)
class PasswordPolicy(Validator):
    """A password-strength rule with SPECIFIC, friendly messages (not an opaque regex).

    Each enabled requirement yields its own message ("Add an uppercase letter.", …). ``check``
    returns the FIRST unmet requirement (Validator contract). ``requirements`` returns the full
    per-rule status for a live checklist UI. Declared by a FieldSchema / policy spec; ENFORCED by
    ``validate_password`` + the setup/auth boundaries — this rule never mutates or stores anything.
    """

    min_length: int = 8
    max_length: int | None = None
    require_upper: bool = False
    require_lower: bool = False
    require_digit: bool = False
    require_symbol: bool = False

    def attrs(self) -> dict[str, Any]:
        a: dict[str, Any] = {"minlength": self.min_length}
        if self.max_length is not None:
            a["maxlength"] = self.max_length
        return a

    def requirements(self, value: str) -> list[tuple[str, bool]]:
        """Per-requirement (message, satisfied) list — for a live checklist UI."""
        out: list[tuple[str, bool]] = [
            (f"At least {self.min_length} characters.", len(value) >= self.min_length),
        ]
        if self.max_length is not None:
            out.append((f"At most {self.max_length} characters.", len(value) <= self.max_length))
        if self.require_upper:
            out.append(("An uppercase letter.", any(c.isupper() for c in value)))
        if self.require_lower:
            out.append(("A lowercase letter.", any(c.islower() for c in value)))
        if self.require_digit:
            out.append(("A number.", any(c.isdigit() for c in value)))
        if self.require_symbol:
            out.append(("A symbol.", any(not c.isalnum() and not c.isspace() for c in value)))
        return out

    def check(self, value: str) -> str | None:
        if not value:
            return None  # `Required` owns emptiness; policy checks a provided value
        for message, ok in self.requirements(value):
            if not ok:
                # Turn the checklist phrasing into an actionable message.
                return f"Password needs: {message[0].lower()}{message[1:]}"
        return None

    def client_rules(self) -> list[dict[str, Any]]:
        """Machine-readable requirement descriptors for the browser checklist. The SAME labels the
        server uses in :meth:`requirements`, plus a ``kind`` + optional ``n`` the JS evaluates so
        the client checklist never re-declares the policy — it reads it off this one source."""
        rules: list[dict[str, Any]] = [
            {
                "id": "min",
                "kind": "min",
                "n": self.min_length,
                "label": f"At least {self.min_length} characters.",
            },
        ]
        if self.max_length is not None:
            rules.append(
                {
                    "id": "max",
                    "kind": "max",
                    "n": self.max_length,
                    "label": f"At most {self.max_length} characters.",
                }
            )
        if self.require_upper:
            rules.append({"id": "upper", "kind": "upper", "label": "An uppercase letter."})
        if self.require_lower:
            rules.append({"id": "lower", "kind": "lower", "label": "A lowercase letter."})
        if self.require_digit:
            rules.append({"id": "digit", "kind": "digit", "label": "A number."})
        if self.require_symbol:
            rules.append({"id": "symbol", "kind": "symbol", "label": "A symbol."})
        return rules
