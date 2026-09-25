"""ContentHeader component — the header at the top of the content pane (NOT the rail).

Page title on the left (the routing framework's ``Page.title`` — single source), an ordered action
row on the right. The action order is FIXED and documented so features slot in predictably:
**1) search → 2) theme switcher → 3) language**. v1 renders only the theme switcher; search and
language are reserved slots (no markup emitted — no empty placeholders).

``actions`` is an ordered list of already-rendered controls the caller supplies in the documented
order; the shell passes ``[ThemeToggle()]`` today.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class ContentHeader(Component):
    """Content-pane header using Beer CSS's ``header > nav`` app-bar idiom: a mobile menu button, an
    ``p.max`` bolded title (``.max`` pushes the trailing actions to the right), then the ordered
    ``actions``. Consistent with the wizard's ``Header`` (also a Beer app bar)."""

    def __init__(self, title: str, *, actions: Sequence[Any] = ()) -> None:
        self.title = title
        self.actions = list(actions)

    def render(self) -> Raw:
        # Mobile-only menu button (left of the title). Hidden on desktop via CSS; opens the drawer.
        menu_btn = tag(
            "button",
            tag("i", "menu"),
            class_="circle transparent mim-nav-open",
            title="Open menu",
            type="button",
            data_mim_nav_open=True,
        )
        # Beer CSS app-bar idiom: header > nav, with a bolded p.max title pushing actions right.
        return tag(
            "header",
            tag(
                "nav",
                menu_btn,
                tag("p", self.title, class_="max mim-page-title bold"),
                *self.actions,
                class_="mim-content-header",
            ),
        )
