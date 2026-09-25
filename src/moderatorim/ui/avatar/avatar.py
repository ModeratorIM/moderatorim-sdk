"""Avatar component — a user's profile image, or a default profile-user icon.

With an ``image``, renders it as a round ``<img>``. With none, renders an inline SVG person icon
inside a circle — an SVG (not a Material Symbol) so it shows offline regardless of the icon font.
"""

from __future__ import annotations

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, tag


class Avatar(Component):
    """A round avatar: the user's ``image`` if given, else a default profile-user icon (an inline
    SVG, so it renders offline without the icon font)."""

    def __init__(self, name: str, *, image: str = "", size: str = "") -> None:
        self.name = name
        self.image = image
        self.size = size  # optional Beer CSS size modifier, e.g. "small" / "large"

    def render(self) -> Raw:
        cls = f"circle mim-avatar {self.size}".strip()
        if self.image:
            return tag("img", src=self.image, alt=self.name, class_=cls)
        # No image → a default profile-user icon. Inline SVG (not a Material Symbol) so it renders
        # offline regardless of whether the icon font is vendored.
        person_svg = Raw(
            '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" '
            'aria-hidden="true" class="mim-avatar-icon">'
            '<path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 '
            '0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>'
        )
        return tag("div", person_svg, class_=cls)
