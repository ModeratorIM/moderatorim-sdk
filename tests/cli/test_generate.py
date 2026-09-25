"""Tests for the `moderatorim generate` family — domain-first, operate-in-app."""

from __future__ import annotations

import os
from pathlib import Path

from moderatorim.cli import main


def _run_in(tmp: Path, argv: list[str]) -> int:
    cwd = Path.cwd()
    os.chdir(tmp)
    try:
        return main(argv)
    finally:
        os.chdir(cwd)


def _make_app(tmp: Path, name: str = "shop") -> Path:
    assert _run_in(tmp, ["create", "app", name]) == 0
    return tmp / name


def _backend_manifest(tmp: Path, name: str = "pg") -> Path:
    root = tmp / name
    root.mkdir()
    (root / "manifest.py").write_text(
        "from moderatorim.sdk import Manifest, UnitType\n"
        f'manifest = Manifest(name="{name}", type=UnitType.BACKEND, register=lambda c: None)\n',
        encoding="utf-8",
    )
    return root


def test_generate_model_writes_domain_package_and_registers(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    rc = _run_in(app, ["generate", "model", "users", "--field", "email:str", "--field", "age:int"])
    assert rc == 0
    model = app / "users" / "model.py"
    assert model.is_file()
    body = model.read_text()
    assert 'table = "shop_users"' in body
    assert "class Users(Model):" in body
    assert '"email": Field(FieldType.STR),' in body
    assert '"age": Field(FieldType.INT),' in body
    # registered in the manifest's models=(...)
    manifest = (app / "manifest.py").read_text()
    assert "from users.model import Users" in manifest
    assert "Users" in manifest and "models=(" in manifest


def test_generate_service_routes_screen_into_same_domain(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    for artifact in ("service", "routes", "screen"):
        assert _run_in(app, ["generate", artifact, "orders"]) == 0
    assert (app / "orders" / "service.py").is_file()
    assert (app / "orders" / "routes.py").is_file()
    assert (app / "orders" / "screen.py").is_file()


def test_generate_test_writes_stub_in_tests(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    assert _run_in(app, ["generate", "test", "billing"]) == 0
    assert (app / "tests" / "test_billing.py").is_file()


def test_generate_refuses_clobber(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    assert _run_in(app, ["generate", "service", "users"]) == 0
    # second identical generate must refuse (file exists)
    assert _run_in(app, ["generate", "service", "users"]) == 1


def test_generate_outside_unit_refused(tmp_path: Path) -> None:
    # no manifest.py in cwd → refused, nothing written
    assert _run_in(tmp_path, ["generate", "model", "users"]) == 2
    assert not (tmp_path / "users").exists()


def test_generate_screen_refused_in_backend(tmp_path: Path) -> None:
    backend = _backend_manifest(tmp_path)
    # backend units may not have screens/routes
    assert _run_in(backend, ["generate", "screen", "widgets"]) == 2
    assert not (backend / "widgets").exists()
    # but service IS allowed in a backend
    assert _run_in(backend, ["generate", "service", "widgets"]) == 0
    assert (backend / "widgets" / "service.py").is_file()


def test_generate_bad_domain_name_refused(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    assert _run_in(app, ["generate", "model", "Users"]) == 2
