"""U2 — validation subsystem tests: render + server-enforce from one declaration."""

from __future__ import annotations

from moderatorim.sdk.validation import (
    Email,
    Max,
    MaxLength,
    Min,
    MinLength,
    OneOf,
    Pattern,
    Required,
    Result,
    build_validators,
    validate_field,
    validate_form,
)
from moderatorim.ui import Input

# --- rules: attrs + check --------------------------------------------------------------


def test_required_attr_and_check() -> None:
    r = Required()
    assert r.attrs() == {"required": True}
    assert r.check("") is not None  # empty fails
    assert r.check("  ") is not None  # whitespace-only fails
    assert r.check("x") is None


def test_minlength_maxlength() -> None:
    assert MinLength(3).attrs() == {"minlength": 3}
    assert MinLength(3).check("ab") is not None
    assert MinLength(3).check("abc") is None
    assert MaxLength(5).check("abcdef") is not None
    assert MaxLength(5).check("abcde") is None


def test_min_max_numbers() -> None:
    assert Min(0).attrs() == {"type": "number", "min": 0}
    assert Min(0).check("-1") is not None
    assert Min(0).check("5") is None
    assert Max(100).check("101") is not None
    assert Min(0).check("abc") == "Must be a number."


def test_pattern_email_oneof() -> None:
    assert Pattern(r"\d+").check("12a") is not None
    assert Pattern(r"\d+").check("123") is None
    assert Email().attrs() == {"type": "email"}
    assert Email().check("nope") is not None
    assert Email().check("a@b.co") is None
    assert OneOf(("a", "b")).check("c") is not None
    assert OneOf(("a", "b")).check("a") is None


# --- Input renders validator attrs -----------------------------------------------------


def test_input_renders_validator_attrs() -> None:
    out = str(Input("name", validators=[MinLength(3), MaxLength(80)]))
    assert 'minlength="3"' in out
    assert 'maxlength="80"' in out


def test_input_number_validator_sets_type() -> None:
    out = str(Input("threshold", validators=[Min(0), Max(100)]))
    assert 'type="number"' in out
    assert 'min="0"' in out and 'max="100"' in out


# --- validate_form: the server-side boundary -------------------------------------------


def test_validate_form_ok() -> None:
    rules = {"name": [Required(), MinLength(3)]}
    result = validate_form(rules, {"name": "hello"})
    assert result.ok


def test_validate_form_collects_errors_by_field() -> None:
    rules = {"name": [Required(), MinLength(3)], "threshold": [Min(0), Max(100)]}
    result = validate_form(rules, {"name": "ab", "threshold": "150"})
    assert not result.ok
    by = result.by_field()
    assert "name" in by and "threshold" in by


def test_server_catches_bypassed_client_constraint() -> None:
    """SECURITY: a client that bypasses the HTML minlength (submits too-short) is still rejected
    server-side — the enforcement is real, not advisory."""
    rules = {"name": [Required(), MinLength(3)]}
    # simulate a crafted POST that ignores the browser's minlength=3
    result = validate_form(rules, {"name": "x"})
    assert not result.ok
    assert result.first("name") is not None


def test_fail_closed_on_unknown_field() -> None:
    rules = {"name": [Required()]}
    result = validate_form(rules, {"name": "ok", "evil": "injected"})
    assert not result.ok
    assert result.first("evil") == "Unexpected field."


# --- build_validators from JSON config -------------------------------------------------


def test_build_validators_from_config() -> None:
    spec = {"required": True, "validation": {"min_length": 3, "max_length": 80}}
    vs = build_validators(spec)
    kinds = {type(v).__name__ for v in vs}
    assert {"Required", "MinLength", "MaxLength"} <= kinds


def test_build_validators_number_and_email() -> None:
    vs = build_validators({"type": "email", "validation": {"min": 0, "max": 100}})
    kinds = {type(v).__name__ for v in vs}
    assert {"Email", "Min", "Max"} <= kinds


def test_validate_field_returns_all_messages() -> None:
    msgs = validate_field("", [Required(), MinLength(3)])
    assert len(msgs) >= 1


def test_empty_result_is_ok() -> None:
    assert Result().ok


def test_password_policy_requirements_and_check() -> None:
    from moderatorim.sdk.validation import PasswordPolicy

    p = PasswordPolicy(min_length=8, require_upper=True, require_digit=True)
    # empty → deferred to Required (no policy error on empty)
    assert p.check("") is None
    # too short → friendly, specific message
    err = p.check("Ab1")
    assert err is not None and "8 characters" in err
    # missing uppercase
    err = p.check("abcdefg1")
    assert err is not None and "uppercase" in err.lower()
    # missing digit
    err = p.check("Abcdefgh")
    assert err is not None and "number" in err.lower()
    # satisfies all → passes
    assert p.check("Abcdefg1") is None
    # requirements() reports per-rule status for a checklist UI
    reqs = dict(p.requirements("Abcdefg1"))
    assert all(reqs.values())
    reqs2 = dict(p.requirements("abc"))
    assert reqs2["At least 8 characters."] is False
    # attrs expose minlength for the browser hint
    assert p.attrs()["minlength"] == 8


def test_password_policy_client_rules_descriptors() -> None:
    from moderatorim.sdk.validation import PasswordPolicy

    p = PasswordPolicy(min_length=8, max_length=72, require_digit=True, require_upper=True)
    rules = p.client_rules()
    kinds = [r["kind"] for r in rules]
    assert kinds == ["min", "max", "upper", "digit"]
    by_id = {r["id"]: r for r in rules}
    assert by_id["min"]["n"] == 8 and by_id["max"]["n"] == 72
    # labels match the server-side checklist phrasing exactly (one source, no drift)
    server = dict(p.requirements("Abcdefg1"))
    for r in rules:
        assert r["label"] in server
