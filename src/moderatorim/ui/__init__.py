"""ModeratorIM UI component library — the single source of truth for BeerCSS UI components.

Both core AND apps import their components from here (``from moderatorim.ui import Card, Button,
Input, tag, ...``). Core no longer hand-rolls its own copies, and apps get the same component
vocabulary core uses — one place to maintain, no duplication.

``moderatorim.ui`` is a top-level peer of ``moderatorim.sdk`` and ``moderatorim.cli`` under the
PEP 420 ``moderatorim`` namespace (shared with ``moderatorim-core``; no package owns the root).
It is SDK-owned by convention and imports only the standard library and ``moderatorim.sdk``
contracts (``Input`` renders an SDK ``Validator``) — never ``moderatorim.core`` — so importing it
never drags in the runtime. A future core contributor must not grab the ``moderatorim.ui`` slot.
"""

from moderatorim.ui.accountmenu import AccountMenu
from moderatorim.ui.alert import Alert
from moderatorim.ui.assets import ui_asset_dir, ui_asset_tags
from moderatorim.ui.avatar import Avatar
from moderatorim.ui.button import Button
from moderatorim.ui.card import Card
from moderatorim.ui.component import Component
from moderatorim.ui.contentheader import ContentHeader
from moderatorim.ui.field import Field
from moderatorim.ui.footer import Footer
from moderatorim.ui.heading import Heading
from moderatorim.ui.html import Raw, attrs, esc, tag
from moderatorim.ui.icon import Icon
from moderatorim.ui.input import Input
from moderatorim.ui.layout import Grid, Nav, Row
from moderatorim.ui.navrail import NavRail
from moderatorim.ui.select import Select
from moderatorim.ui.stepper import Stepper

__all__ = [
    # primitives
    "Component",
    "Raw",
    "attrs",
    "esc",
    "tag",
    # assets (shipped BeerCSS/MDC/base CSS+JS; host mounts + emits refs)
    "ui_asset_dir",
    "ui_asset_tags",
    # components
    "AccountMenu",
    "Alert",
    "Avatar",
    "Button",
    "Card",
    "ContentHeader",
    "Field",
    "Footer",
    "Grid",
    "Heading",
    "Icon",
    "Input",
    "Nav",
    "NavRail",
    "Row",
    "Select",
    "Stepper",
]
