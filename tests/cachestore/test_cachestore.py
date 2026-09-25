"""Contract tests for the cachestore domain (the CacheStore port)."""

from __future__ import annotations

from moderatorim.sdk import CacheStore


def test_cachestore_is_runtime_checkable_protocol() -> None:
    # A bare object is not a CacheStore; a shape-complete class is (structural typing).
    assert not isinstance(object(), CacheStore)

    class Fake:
        async def get(self, key: str) -> str | None: ...
        async def set(self, key: str, value: str, *, ttl: int | None = None) -> None: ...
        async def delete(self, key: str) -> None: ...
        async def incr(self, key: str, *, amount: int = 1) -> int: ...  # type: ignore[empty-body]
        async def expire(self, key: str, ttl: int) -> None: ...
        async def exists(self, key: str) -> bool: ...  # type: ignore[empty-body]

    assert isinstance(Fake(), CacheStore)


def test_cachestore_importable_from_root() -> None:
    # It is part of the flat public API, imported from the package root, not a deep module.
    import moderatorim.sdk

    assert moderatorim.sdk.CacheStore is CacheStore
