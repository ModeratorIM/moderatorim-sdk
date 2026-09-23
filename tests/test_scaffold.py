"""Scaffold smoke test — replaced by real contract tests as modules are moved in (SDK P1+)."""

import moderatorim.sdk


def test_sdk_package_imports() -> None:
    assert hasattr(moderatorim.sdk, "__all__")
