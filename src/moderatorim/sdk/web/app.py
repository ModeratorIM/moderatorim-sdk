"""The ``App`` routing facade — pure registration. Core's adapter consumes ``App.routes``."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


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

    PURE registration — holds route declarations, nothing runtime. Dispatch (build Ctx, enforce
    permission, render, wire cookies) is core's ``adapter.build_routes(app, …)``.
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
