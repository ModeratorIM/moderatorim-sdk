"""The routing facade — the public web surface app authors touch.

App authors register handlers with ``@app.page`` / ``@app.action`` / ``@app.post`` and return
``Page`` / ``redirect(...)`` / ``Fragment``; they never name Starlette, ``Request``, ``Response``,
or htmx headers. This module holds ONLY the facade: the primitives an app returns, the ``Ctx``
handle it receives, and the ``App`` that records route declarations. The dispatch adapter that turns
those declarations into real HTTP responses — enforcing permissions, rendering, wiring cookies —
lives in core (``moderatorim.core.web.adapter``); it reads an ``App``'s :attr:`App.routes` and
supplies the runtime.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing only
    from moderatorim.sdk.datastore import DataStore

# A rendered page body is a list of UI-SDK components or raw HTML strings; kept as Any so the
# renderer (core) handles both without the SDK importing a component base.
Content = list[Any]


@dataclass
class Page:
    """A full page a ``@app.page`` handler returns. On a normal GET the framework wraps it in the
    shell → a full HTML document; on an ``HX-Request`` it renders only the body fragment and sets
    ``HX-Push-Url`` centrally (so the URL ↔ DOM stay in sync without per-button ``hx-push-url``)."""

    title: str
    content: Content
    permission: str | None = None


@dataclass
class Redirect:
    """A mutate-then-navigate result a ``@app.action`` handler returns. The framework emits
    ``HX-Redirect: url`` for htmx requests and a ``303 → url`` for plain ones. ``replace=True`` also
    sets ``X-Mim-Replace`` so the client replaces history instead of pushing — used when crossing
    the auth boundary (after sign-in the back button must not reach the sign-in screen)."""

    url: str
    replace: bool = False


def redirect(url: str, *, replace: bool = False) -> Redirect:
    """Return a navigation result (``HX-Redirect`` for htmx, ``303`` for plain requests).
    ``replace=True`` requests a history REPLACE rather than a push."""
    return Redirect(url, replace=replace)


@dataclass
class Fragment:
    """A swap-in-place result a ``@app.post`` handler returns (no navigation). ``html`` is a raw
    HTML string or a UI-SDK component the framework renders."""

    html: Any


@dataclass
class Rendered:
    """Swap-in-place content with an explicit HTTP status — e.g. a 404 body for a disabled route,
    or a re-rendered screen. A bare :class:`Fragment` (or component/str) implies status 200."""

    html: Any
    status: int = 200


@dataclass
class Ctx:
    """Per-request context the framework populates and hands to a handler, so handlers stay
    module-level instead of closing over app-construction state.

    - ``config``  — the resolved runtime config (opaque to the SDK; ``Any``).
    - ``user``    — the resolved ACTIVE user, or None.
    - ``store``   — the configured DataStore, or None if unconfigured.
    - ``request`` — the underlying request object (escape hatch; app code should rarely need it).
    - ``can``     — a ``can(permission)->bool`` predicate for the current user (read-gating).
    - ``authz``   — the RBAC management handle (define_role / grant_role_to_group / …) for apps that
                    MANAGE permissions (e.g. admin). Both are supplied by core at request build.
    - session/cookie mutations are recorded and applied to the outgoing response by the adapter.
    """

    config: Any
    request: Any
    user: Any | None = None
    store: DataStore | None = None
    can: Callable[[str], bool] = field(default=lambda _p: False)
    authz: Any | None = None
    # Recorded cookie intent applied by the adapter after the handler returns.
    _set_session: str | None = field(default=None, repr=False)
    _clear_session: bool = field(default=False, repr=False)
    _extra_cookies: list[tuple[str, str, str, int | None]] = field(default_factory=list, repr=False)

    def set_session(self, token: str) -> None:
        """Set the session cookie on the outgoing response."""
        self._set_session = token
        self._clear_session = False

    def clear_session(self) -> None:
        """Clear the session cookie on the outgoing response (logout)."""
        self._clear_session = True
        self._set_session = None

    def set_cookie(
        self, name: str, value: str, *, path: str = "/", max_age: int | None = None
    ) -> None:
        """Record a non-session cookie to set on the outgoing response (httponly, samesite=lax,
        secure from the request scheme). Used e.g. for the setup installation-lock cookie."""
        self._extra_cookies.append((name, value, path, max_age))

    async def form(self) -> dict[str, str]:
        """Parse the urlencoded request body into a flat {field: value} dict (last value wins)."""
        from urllib.parse import parse_qs

        raw = (await self.request.body()).decode()
        return {k: v[0] for k, v in parse_qs(raw).items()}

    def query(self, key: str, default: str = "") -> str:
        """Read a query-string parameter."""
        value: str = self.request.query_params.get(key, default)
        return value


class Kind(Enum):
    PAGE = auto()
    ACTION = auto()
    POST = auto()


@dataclass
class RouteDef:
    """A recorded route declaration. Core's adapter turns each into a real HTTP route."""

    path: str
    methods: tuple[str, ...]
    handler: Callable[..., Any]
    kind: Kind
    title: str | None = None
    permission: str | None = None
    nav: str | None = None


class App:
    """A collection of self-registering routes. Core owns one; each mounted app owns its own, and
    core's adapter collects each App's :attr:`routes` into the live application.

    This is PURE registration — it holds route declarations and nothing runtime. The dispatch
    (build Ctx, enforce permission, render, wire cookies) is core's
    ``adapter.build_routes(app, …)``.
    """

    def __init__(self) -> None:
        self._routes: list[RouteDef] = []

    def page(
        self,
        path: str,
        *,
        title: str | None = None,
        permission: str | None = None,
        nav: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._routes.append(
                RouteDef(path, ("GET",), fn, Kind.PAGE, title=title, permission=permission, nav=nav)
            )
            return fn

        return deco

    def action(
        self, path: str, *, methods: tuple[str, ...] = ("POST",), permission: str | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._routes.append(RouteDef(path, methods, fn, Kind.ACTION, permission=permission))
            return fn

        return deco

    def post(
        self, path: str, *, permission: str | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._routes.append(RouteDef(path, ("POST",), fn, Kind.POST, permission=permission))
            return fn

        return deco

    @property
    def routes(self) -> list[RouteDef]:
        """All recorded route declarations (core's adapter consumes these)."""
        return list(self._routes)

    @property
    def nav_routes(self) -> list[RouteDef]:
        """Routes that declared ``nav=`` — shown only when their permission check passes."""
        return [rd for rd in self._routes if rd.nav is not None]
