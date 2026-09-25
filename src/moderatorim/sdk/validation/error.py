"""Validation error type (U2.2)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidationError:
    """One validation failure: which field, and a human-readable message."""

    field: str
    message: str
