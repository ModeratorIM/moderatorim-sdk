"""ModeratorIM app SDK — the contract kernel external apps build against.

An app imports ONLY from this package (``from moderatorim.sdk import Manifest, Model, ...``); it
never imports ``moderatorim.core``. Core implements these contracts and injects live handles (the
``Ctx``) at runtime, so an app reaches core's behavior without depending on it.

``moderatorim`` is a PEP 420 namespace shared with ``moderatorim-core`` — this package owns only
``moderatorim.sdk``.
"""

from moderatorim.sdk.bus import (
    Action,
    ActionKind,
    Event,
    EventBus,
    EventKind,
    Handler,
)
from moderatorim.sdk.datastore import (
    DataStore,
    Filter,
    FilterOp,
    Record,
)
from moderatorim.sdk.manifest import (
    Manifest,
    NavEntry,
    UnitType,
)
from moderatorim.sdk.models import (
    Extends,
    Field,
    FieldType,
    Model,
    ResolvedColumn,
    ResolvedSchema,
    enum,
    list_of,
    ref,
)

__all__ = [
    # models
    "Model",
    "Field",
    "FieldType",
    "Extends",
    "ResolvedColumn",
    "ResolvedSchema",
    "ref",
    "enum",
    "list_of",
    # datastore port
    "DataStore",
    "Filter",
    "FilterOp",
    "Record",
    # bus
    "Event",
    "EventKind",
    "Action",
    "ActionKind",
    "EventBus",
    "Handler",
    # manifest
    "Manifest",
    "UnitType",
    "NavEntry",
    # web facade (App, Ctx, Page, ...) is added in SDK P2.
]
