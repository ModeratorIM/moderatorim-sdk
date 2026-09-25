"""ThemeToggle component — the night-mode switch button.

A Beer CSS icon button carrying the SAME data hooks the auth shell's pinned toggle uses
(``data-mim-theme-toggle`` + ``data-mim-theme-icon``), so the existing swap-safe ``theme-toggle.js``
drives it unchanged — no new JS. Used as a content-header action, but self-contained enough to drop
anywhere.
"""

from __future__ import annotations

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class ThemeToggle(Component):
    """A night-mode toggle icon button (driven by theme-toggle.js via shared data hooks)."""

    def render(self) -> Raw:
        return tag(
            "button",
            tag("i", "dark_mode", data_mim_theme_icon=True),
            class_="circle transparent mim-theme-toggle",
            title="Toggle night mode",
            type="button",
            data_mim_theme_toggle=True,
        )
