"""Contract tests for the registry domain (Manifest, UnitType, NavEntry)."""

from __future__ import annotations

import pytest

from moderatorim.sdk import Manifest, NavEntry, UnitType


def test_manifest_basics_and_routes_hook() -> None:
    m = Manifest(
        name="widget",
        type=UnitType.APP,
        register=lambda core: None,
        nav=(NavEntry("Widget", "/widget", "star"),),
        routes=lambda app: None,
    )
    assert m.title == "Widget" and m.routes is not None
    with pytest.raises(TypeError, match="routes must be callable"):
        Manifest(name="bad", type=UnitType.APP, register=lambda c: None, routes=1)  # type: ignore[arg-type]


def test_manifest_name_validation() -> None:
    with pytest.raises(ValueError, match="lowercase"):
        Manifest(name="Widget", type=UnitType.APP, register=lambda c: None)


def test_nav_entry_icon_is_asset() -> None:
    assert NavEntry("A", "/a", "star").icon_is_asset is False
    assert NavEntry("A", "/a", "/static/a.svg").icon_is_asset is True
