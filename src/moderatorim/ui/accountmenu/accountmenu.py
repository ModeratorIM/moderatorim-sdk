"""AccountMenu component — the signed-in user's block at the bottom of the rail + its popover.

A button showing the avatar + name (+ muted email) that opens a menu on click. The menu is an
anchored dropdown positioned within the account block (opens UPWARD, since the block sits at the
bottom of the rail), toggled by a swap-safe delegated handler on ``[data-mim-account-toggle]`` in
``nav-collapse.js`` (re-applied after htmx body-swaps). Native ``popover`` was avoided because it
renders in the browser top-layer centered in the viewport with no anchor to the button.

Items: Profile, Settings, Admin (only when ``is_admin``), then a divider and Sign out (an htmx
``POST /logout``). The avatar is passed in already-rendered so this component composes without
importing the Avatar component (UI SDK isolation).
"""

from __future__ import annotations

from typing import Any

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag

_MENU_ID = "mim-account-menu"


class AccountMenu(Component):
    """Account block (avatar + name) + a native-popover menu. ``avatar`` is pre-rendered markup."""

    def __init__(
        self,
        name: str,
        *,
        email: str = "",
        avatar: Any = "",
        is_admin: bool = False,
    ) -> None:
        self.name = name
        self.email = email
        self.avatar = avatar
        self.is_admin = is_admin

    def _identity(self) -> Raw:
        lines: list[object] = [tag("span", self.name, class_="mim-account-name")]
        if self.email:
            lines.append(tag("span", self.email, class_="mim-account-email mim-rail-muted"))
        return tag("div", *lines, class_="mim-account-identity")

    def _link(self, label: str, path: str, icon: str) -> Raw:
        return tag(
            "a",
            tag("i", icon),
            tag("span", label),
            href=path,
            class_="mim-account-link",
            hx_get=path,
            hx_target="body",
        )

    def render(self) -> Raw:
        items: list[object] = [
            self._link("Profile", "/profile", "person"),
            self._link("Settings", "/settings", "settings"),
        ]
        if self.is_admin:
            items.append(self._link("Admin", "/admin", "admin_panel_settings"))
        items.append(tag("div", class_="mim-account-divider"))
        # Sign out is a POST (clears the session server-side), not a navigation link.
        items.append(
            tag(
                "button",
                tag("i", "logout"),
                tag("span", "Sign out"),
                class_="mim-account-link mim-account-signout",
                type="button",
                hx_post="/logout",
                hx_target="body",
            )
        )
        # Beer CSS native <menu>: `top` opens upward, `no-wrap` gives it a real width; Beer's own
        # CSS owns positioning/elevation/surface. The menu is a SIBLING of the trigger (not nested
        # inside the <button> — that would be invalid interactive-content nesting) within a
        # positioned wrapper. Our swap-safe handler (nav-collapse.js) toggles Beer's `.active`.
        menu = tag("menu", *items, id=_MENU_ID, class_="top no-wrap mim-account-menu")
        button = tag(
            "button",
            self.avatar,
            self._identity(),
            tag("i", "expand_more", class_="mim-account-caret"),
            class_="mim-account",
            type="button",
            data_mim_account_toggle=True,
            aria_haspopup="menu",
            aria_expanded="false",
        )
        return tag("div", button, menu, class_="mim-account-block")
