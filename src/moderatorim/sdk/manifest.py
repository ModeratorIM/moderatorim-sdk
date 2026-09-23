"""The ``Manifest`` contract — how a unit declares itself to the core.

Every installable unit (an app, a platform adapter, a backend adapter) exposes a module-level
``manifest`` of this type. The core reads it to know the unit's name, type, dependencies, the
models it contributes, the inheritance and routes it declares, its permissions/roles, and its
store metadata — without importing the unit's implementation until boot.

A unit's ``register(core)`` hook is invoked once at boot, in dependency order, after its models are
provisioned — where it wires services, subscribes to events, and mounts UI. Its optional
``routes(app)`` hook adds pages to the web router. Both touch only the SDK surface, never core.
"""

from __future__ import annotations

import builtins
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from moderatorim.sdk.models import Extends, Model


class UnitType(Enum):
    """The three kinds of installable unit, ordered by layer (lower value = lower layer).

    A unit may depend only on units at the same or a lower layer, and app→app dependencies must be
    acyclic. Backends and platforms sit below apps and never depend on an app.
    """

    BACKEND = 0  # persistence/auth/storage adapter (implements data/file/auth ports)
    PLATFORM = 1  # messaging-channel adapter (implements the platform port)
    APP = 2  # feature package (may depend on other apps)


@dataclass(frozen=True, slots=True)
class NavEntry:
    """A left-rail navigation entry an app contributes for the authenticated shell.

    ``icon`` is either a Material Symbol name (rendered as ``<i>``) or a path to the app's own icon
    asset (rendered as ``<img>`` — a value containing ``/`` or ending in an image extension is
    treated as an asset). ``permission`` gates visibility (None = always visible). ``order`` sorts
    entries within the rail (lower first); ties break on ``label``.
    """

    label: str
    path: str
    icon: str = ""
    permission: str | None = None
    order: int = 100
    badge: str | int | None = None  # optional right-aligned counter/badge (e.g. unread count)

    @property
    def icon_is_asset(self) -> bool:
        """True when ``icon`` is an image asset path (``<img>``) rather than a Material Symbol."""
        return "/" in self.icon or self.icon.endswith((".svg", ".png", ".webp"))


@dataclass(frozen=True, slots=True)
class Manifest:
    """A unit's self-declaration.

    ``register`` is the one-time boot hook. ``dependency`` names OTHER units this one requires (by
    manifest name) — for an app, these are other apps. ``models`` are the unit's own model classes;
    ``extends`` are the inheritance links it declares against lower units' models. ``routes`` is the
    optional ``register_routes(app)`` hook that adds the unit's pages to the web router.
    """

    name: str
    type: UnitType
    register: Callable[[Any], None]
    version: str = "0.0.0"
    display_name: str = ""  # human-facing name for UI (e.g. "Postgres"); defaults to ``name``
    dependency: tuple[str, ...] = ()
    provides: tuple[str, ...] = ()
    # ``builtins.type`` (not bare ``type``): the ``type`` FIELD above shadows the builtin inside
    # this class under string-evaluated annotations, so we qualify it to reach the real builtin.
    models: tuple[builtins.type[Model], ...] = ()
    extends: tuple[Extends, ...] = ()
    store_metadata: dict[str, Any] = field(default_factory=dict)
    nav: tuple[NavEntry, ...] = ()  # left-rail entries this unit contributes (apps only)
    # RBAC: the permission grants this unit DEFINES (its {app}.{resource}.{action} catalog) and the
    # default roles it seeds (role name -> list of grants). The core registers these at boot; the
    # unit only declares.
    permissions: tuple[str, ...] = ()
    default_roles: dict[str, tuple[str, ...]] = field(default_factory=dict)
    # Route contribution: an optional hook ``register_routes(app)`` the core calls at build time
    # with the web ``App`` facade, so an app can add its ``@app.page/action/post`` pages. Kept
    # SDK-only — the app touches only the ``web`` facade. Apps declaring routes but no models are
    # fine.
    routes: Callable[[Any], None] | None = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Manifest.name is required")
        if not self.name.islower() or " " in self.name:
            raise ValueError(f"Manifest.name must be lowercase, no spaces: {self.name!r}")
        if not callable(self.register):
            raise TypeError("Manifest.register must be callable (the boot hook)")
        if self.routes is not None and not callable(self.routes):
            raise TypeError("Manifest.routes must be callable (register_routes(app)) or None")
        if self.name in self.dependency:
            raise ValueError(f"unit {self.name!r} cannot depend on itself")
        if len(set(self.dependency)) != len(self.dependency):
            raise ValueError(f"unit {self.name!r} has duplicate dependencies")

    @property
    def title(self) -> str:
        """Human-facing name for UI: the explicit ``display_name`` if set, else a capitalized form
        of the machine ``name`` (``postgres`` → ``Postgres``)."""
        return self.display_name or self.name.capitalize()
