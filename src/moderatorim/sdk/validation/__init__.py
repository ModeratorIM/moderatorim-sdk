"""Validation subsystem (U2) — render + server-enforce from ONE declaration.

A field's rules are declared once (as :mod:`rules` validators) and used two ways that can never
drift: (1) **rendered** as HTML attributes for browser UX, and (2) **enforced server-side** on
POST as the real security boundary. Server enforcement is mandatory — a form built via the SDK
is validated on submit; a bypassed client-side constraint is still caught here.
"""

from moderatorim.sdk.validation.build import build_validators
from moderatorim.sdk.validation.error import ValidationError
from moderatorim.sdk.validation.result import Result
from moderatorim.sdk.validation.rules import (
    Email,
    Max,
    MaxLength,
    Min,
    MinLength,
    OneOf,
    PasswordPolicy,
    Pattern,
    Required,
    Validator,
)
from moderatorim.sdk.validation.validator import validate_field, validate_form

__all__ = [
    "Validator",
    "Required",
    "MinLength",
    "MaxLength",
    "Min",
    "Max",
    "Pattern",
    "Email",
    "OneOf",
    "PasswordPolicy",
    "ValidationError",
    "Result",
    "validate_field",
    "validate_form",
    "build_validators",
]
