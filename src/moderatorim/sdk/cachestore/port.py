"""The ``CacheStore`` port — ephemeral key/value storage behind a narrow interface.

The core caches its own data (sessions, rate-limit counters, short-lived values) against this
port. It is deliberately narrow — string values, TTL, and an atomic counter — so every
implementation is trivial and no caller can smuggle backend-specific semantics through it.

Unlike :class:`~moderatorim.sdk.datastore.DataStore`, a ``CacheStore`` is NOT a discovered
"backend" unit selected in the setup wizard: it is caching INFRASTRUCTURE the core instantiates
from configuration (an in-memory default, or Redis when a URL is configured). The port lives in
the SDK so it is a frozen public contract a third party could also implement.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class CacheStore(Protocol):
    """Ephemeral key/value cache port. Implementations back it in-process or with Redis.

    Values are strings — callers serialize richer types themselves, keeping the port trivially
    implementable everywhere. TTLs are seconds; a key with no TTL persists until deleted.
    """

    async def get(self, key: str) -> str | None:
        """Return the value for ``key``, or ``None`` if absent or expired."""
        ...

    async def set(self, key: str, value: str, *, ttl: int | None = None) -> None:
        """Store ``value`` under ``key``. With ``ttl`` (seconds), the key expires after it."""
        ...

    async def delete(self, key: str) -> None:
        """Remove ``key``. A no-op when the key is absent."""
        ...

    async def incr(self, key: str, *, amount: int = 1) -> int:
        """Atomically add ``amount`` to the integer at ``key`` (0 if absent); return the result."""
        ...

    async def expire(self, key: str, ttl: int) -> None:
        """Set ``key`` to expire after ``ttl`` seconds. A no-op when the key is absent."""
        ...

    async def exists(self, key: str) -> bool:
        """Return whether ``key`` is present and unexpired."""
        ...
