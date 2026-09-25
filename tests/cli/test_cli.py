"""Tests for the `moderatorim` CLI — v1 `create app`."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest

from moderatorim.cli import main


def _run_in(tmp: Path, argv: list[str]) -> int:
    cwd = Path.cwd()
    os.chdir(tmp)
    try:
        return main(argv)
    finally:
        os.chdir(cwd)


def test_create_app_writes_expected_tree(tmp_path: Path) -> None:
    rc = _run_in(
        tmp_path,
        ["create", "app", "widget", "--display-name", "Widget", "--description", "A test app"],
    )
    assert rc == 0
    app = tmp_path / "widget"
    assert (app / "__init__.py").is_file()
    assert (app / "manifest.py").is_file()
    assert (app / "README.md").is_file()
    assert (app / "tests" / "__init__.py").is_file()
    assert (app / "tests" / "test_manifest.py").is_file()
    # NO starter domain package named after the app (that collided app-vs-domain); domains come
    # from `generate <kind> <domain>`.
    assert not (app / "widget").exists()
    # NO packaging config — apps are addons, not distributions
    assert not (app / "pyproject.toml").exists()
    # README carries the description + display name
    readme = (app / "README.md").read_text()
    assert "Widget" in readme and "A test app" in readme
    # manifest.py declares the name/type/version
    manifest_src = (app / "manifest.py").read_text()
    assert 'name="widget"' in manifest_src
    assert "UnitType.APP" in manifest_src


def test_generated_manifest_imports_and_names_itself(tmp_path: Path) -> None:
    rc = _run_in(tmp_path, ["create", "app", "gizmo"])
    assert rc == 0
    # put the temp dir on sys.path and import the generated app, then read its manifest
    sys.path.insert(0, str(tmp_path))
    try:
        mod = importlib.import_module("gizmo")
        assert mod.manifest.name == "gizmo"
        from moderatorim.sdk import UnitType

        assert mod.manifest.type is UnitType.APP
        assert callable(mod.manifest.register)
    finally:
        sys.path.remove(str(tmp_path))
        for name in list(sys.modules):
            if name == "gizmo" or name.startswith("gizmo."):
                del sys.modules[name]


def test_create_app_default_display_name_titlecases(tmp_path: Path) -> None:
    rc = _run_in(tmp_path, ["create", "app", "my_product"])
    assert rc == 0
    manifest_src = (tmp_path / "my_product" / "manifest.py").read_text()
    assert 'display_name="My Product"' in manifest_src


def test_create_app_refuses_existing_dir(tmp_path: Path) -> None:
    (tmp_path / "widget").mkdir()
    rc = _run_in(tmp_path, ["create", "app", "widget"])
    assert rc == 2
    # nothing scaffolded into the pre-existing dir
    assert not (tmp_path / "widget" / "manifest.py").exists()


@pytest.mark.parametrize("bad", ["Widget", "my-product", "1widget", "my product", ""])
def test_create_app_refuses_bad_name(tmp_path: Path, bad: str) -> None:
    rc = _run_in(tmp_path, ["create", "app", bad])
    assert rc == 2


def test_no_subcommand_returns_error(tmp_path: Path) -> None:
    assert _run_in(tmp_path, []) == 2
