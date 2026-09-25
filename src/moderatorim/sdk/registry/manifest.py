"""The ``Manifest`` contract — how a unit declares itself to the core.

Every installable unit exposes a module-level ``manifest`` of this type. The core reads it for the
unit's name, type, dependencies, models, inheritance, routes, permissions/roles, and store metadata
— without importing the unit's implementation until boot. The ``register(core)`` hook wires
services / subscribes to events; the optional ``routes(app)`` hook adds pages. Both touch only the
SDK surface, never core.
"""

from __future__ import annotations

import builtins
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from moderatorim.sdk.models import Extends, Model


class UnitType(Enum):
    """The three kinds of installable unit, ordered by layer (lower value = lower layer)."""

    BACKEND = 0  # persistence/auth/storage adapter
    PLATFORM = 1  # messaging-channel adapter
    APP = 2  # feature package (may depend on other apps)


@dataclass(frozen=True, slots=True)
class NavEntry:
    """A left-rail navigation entry an app contributes for the authenticated shell.

    ``icon`` is a Material Symbol name (``<i>``) or a path to the app's own icon asset (``<img>`` —
    a value with ``/`` or an image extension). ``permission`` gates visibility (None = always).
    ``order`` sorts entries (lower first); ties break on ``label``.
    """

    label: str
    path: str
    icon: str = ""
    permission: str | None = None
    order: int = 100
    badge: str | int | None = None
    # Placement: when True this entry is the app's ENTRY POINT in the account popup menu (gated by
    # ``permission``) instead of a tile in the global launcher rail. The app's other nav entries
    # still form its in-app (app-scoped) rail. Use for a management app reached via the account
    # menu rather than launched from the rail (e.g. admin). Default False = a launcher tile.
    is_popup_menu: bool = False

    @property
    def icon_is_asset(self) -> bool:
        """True when ``icon`` is an image asset path (``<img>``) rather than a Material Symbol."""
        return "/" in self.icon or self.icon.endswith((".svg", ".png", ".webp"))


@dataclass(frozen=True, slots=True)
class Manifest:
    """A unit's self-declaration.

    ``register`` is the one-time boot hook. ``dependency`` names OTHER units this requires (by
    manifest name). ``models`` are the unit's own model classes; ``extends`` the inheritance links.
    ``routes`` is the optional ``register_routes(app)`` hook adding the unit's pages to the router.
    """

    name: str
    type: UnitType
    register: Callable[[Any], None]
    version: str = "0.0.0"
    display_name: str = ""
    dependency: tuple[str, ...] = ()
    provides: tuple[str, ...] = ()
    # ``builtins.type`` (not bare ``type``): the ``type`` FIELD above shadows the builtin under
    # string-evaluated annotations, so we qualify it to reach the real builtin.
    models: tuple[builtins.type[Model], ...] = ()
    extends: tuple[Extends, ...] = ()
    store_metadata: dict[str, Any] = field(default_factory=dict)
    nav: tuple[NavEntry, ...] = ()
    # Stylesheet filenames the app ships in its static dir, injected into the <head> by core when
    # one of the app's pages is served (served from /static/apps/{name}/<file>). App-owned theming:
    # the app declares + ships the CSS; core serves it and links it. e.g. ("admin.css",).
    styles: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    # Roles this unit declares (seeded into the core RBAC catalog at boot): {role_name: (grants,)}.
    # Renamed from `default_roles` — the seeding-default semantics live in the docs, not the field.
    roles: dict[str, tuple[str, ...]] = field(default_factory=dict)
    # System users this unit ships: each maps a system-user NAME ("{app}.{user_name}",
    # e.g. "cron.user") to the group names it belongs to. Boot/install seeds each as a
    # type="system", un-loginable core_user and places it in those groups, so the unit's userless
    # work (event-bus subscribers, cron, webhooks, boot hooks) runs AS a real, least-privilege RBAC
    # principal. Core validates the "{app}" ownership prefix and seeds them (apps declare, core
    # decides) — the SDK only carries the declaration.
    system_users: dict[str, tuple[str, ...]] = field(default_factory=dict)
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
        """Human-facing name: the explicit ``display_name`` if set, else a capitalized ``name``."""
        return self.display_name or self.name.capitalize()
