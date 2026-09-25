"""Header component — a generic BeerCSS app bar.

The BeerCSS ``<header><nav>`` app-bar idiom as a reusable primitive: an optional ``leading`` slot
(a menu/back button the caller supplies), a title pushed left, and a right-aligned ``actions`` row
(search boxes, buttons — any already-rendered controls). Purely generic — no ModeratorIM classes,
routes, or navigation hooks — so an app composes its own top bar:

    Header("Members", actions=[Button("Invite", icon="add")])

Core's own chrome (the content-pane header with the rail's mobile-menu button, the wizard's
branded bar) composes THIS and adds its specifics.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class Header(Component):
    """A BeerCSS app bar: ``<header><nav>`` with an optional ``leading`` control, a ``.max`` title
    that pushes the trailing ``actions`` to the right, and the ordered ``actions`` row. All slots
    take already-rendered controls (components / ``Raw`` / str)."""

    def __init__(
        self,
        title: str = "",
        *,
        actions: Sequence[Any] = (),
        leading: Any = None,
        class_: str = "",
        title_class: str = "",
    ) -> None:
        self.title = title
        self.actions = list(actions)
        self.leading = leading
        self.class_ = class_
        self.title_class = title_class

    def render(self) -> Raw:
        children: list[Any] = []
        if self.leading is not None:
            children.append(self.leading)
        # `.max` on the title cell pushes the trailing actions to the right (BeerCSS idiom); a host
        # may add its own styling hook via `title_class` / `class_` without this staying generic.
        title_cls = f"max bold {self.title_class}".strip()
        children.append(tag("p", self.title, class_=title_cls))
        children.extend(self.actions)
        nav = tag("nav", *children, class_=self.class_) if self.class_ else tag("nav", *children)
        return tag("header", nav)
