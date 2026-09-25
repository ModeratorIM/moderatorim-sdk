"""ModeratorIM UI component library — the single source of truth for BeerCSS UI components.

Both core AND apps import their components from here (``from moderatorim.ui import tag, Component,
esc, Raw``). Core no longer hand-rolls its own copies, and apps get the same component vocabulary
core uses — one place to maintain, no duplication.

``moderatorim.ui`` is a top-level peer of ``moderatorim.sdk`` and ``moderatorim.cli`` under the
PEP 420 ``moderatorim`` namespace (shared with ``moderatorim-core``; no package owns the root).
It is SDK-owned by convention and imports ONLY the standard library — never ``moderatorim.core``
or ``moderatorim.sdk`` runtime — so importing it never drags in contracts or the runtime. A future
core contributor must not grab the ``moderatorim.ui`` top-level slot.
"""

from moderatorim.ui.component import Component
from moderatorim.ui.html import Raw, attrs, esc, tag

__all__ = [
    "Component",
    "Raw",
    "attrs",
    "esc",
    "tag",
]
