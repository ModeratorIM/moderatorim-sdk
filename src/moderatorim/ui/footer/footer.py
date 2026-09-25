"""Footer component — the app page footer (Beer CSS)."""

from __future__ import annotations

from datetime import UTC, datetime

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class Footer(Component):
    """The page footer: a centered ``© <year> <brand> · All rights reserved`` line. The year is
    computed at render time (UTC), so it stays current without a rebuild."""

    def __init__(self, brand: str = "ModeratorIM") -> None:
        self.brand = brand

    def render(self) -> Raw:
        year = datetime.now(UTC).year
        text = f"© {year} {self.brand} · All rights reserved."
        # Beer CSS: `<footer>` element, small muted centered text.
        return tag(
            "footer",
            tag("span", text, class_="small-text"),
            class_="center-align mim-footer",
        )
