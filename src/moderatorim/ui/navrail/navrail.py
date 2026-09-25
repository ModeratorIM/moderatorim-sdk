"""NavRail component — the left-rail navigation ITEMS for the authenticated shell.

Renders the list of nav links that go inside ``app_shell_authenticated``'s ``nav.left`` rail (the
``<nav>`` wrapper + brand + account block are the shell's; this is just the items slot). Each item
is a Beer CSS rail link: an icon (an ``<img>`` for an app-supplied asset, or an ``<i>`` Material
Symbol for a core entry), the label, and a ``.tooltip right`` (the only label source when the rail
is collapsed to mini/``small``). The active route gets Beer CSS's ``.active``.

Items are duck-typed (``label``/``path``/``icon``/``icon_is_asset``/``permission``) so this stays
decoupled from the registry's ``NavEntry`` — any object with those attributes renders.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class NavRail(Component):
    """The rail's nav items. ``items`` is the resolved, ordered, permission-filtered list (the
    registry produces it); ``current_path`` marks the ``.active`` item. Items are duck-typed:
    any object with ``label``/``path``/``icon``/``icon_is_asset`` renders (the registry's
    ``NavEntry`` satisfies this without this module importing it)."""

    def __init__(self, items: Sequence[Any], *, current_path: str = "/") -> None:
        self.items = items
        self.current_path = current_path

    def _icon(self, item: Any) -> Raw:
        if item.icon_is_asset:
            return tag("img", src=item.icon, alt="", class_="mim-nav-icon")
        return tag("i", item.icon or "circle")

    def render(self) -> Raw:
        links: list[object] = []
        for item in self.items:
            active = " active" if item.path == self.current_path else ""
            children: list[object] = [
                self._icon(item),
                tag("span", item.label, class_="max mim-nav-label"),
            ]
            badge = getattr(item, "badge", None)
            if badge is not None and badge != "":
                children.append(tag("span", str(badge), class_="mim-nav-badge"))
            children.append(tag("div", item.label, class_="tooltip right"))
            links.append(
                tag(
                    "a",
                    *children,
                    href=item.path,
                    class_=f"mim-nav-item{active}",
                    hx_get=item.path,
                    hx_target="body",
                )
            )
        return tag("div", *links, class_="mim-nav-items")
