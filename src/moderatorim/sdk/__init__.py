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
    FilterList,
    FilterOp,
    Record,
    RecordList,
)
from moderatorim.sdk.models import (
    ID_FIELD,
    SOFT_DELETE_FIELD,
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
from moderatorim.sdk.registry import (
    Manifest,
    NavEntry,
    UnitType,
)
from moderatorim.sdk.web import (
    App,
    Ctx,
    Fragment,
    Kind,
    Page,
    Redirect,
    Rendered,
    RouteDef,
    redirect,
)

__all__ = [
    # models
    "Model",
    "Field",
    "FieldType",
    "Extends",
    "ResolvedColumn",
    "ResolvedSchema",
    "ID_FIELD",
    "SOFT_DELETE_FIELD",
    "ref",
    "enum",
    "list_of",
    # datastore port
    "DataStore",
    "Filter",
    "FilterList",
    "FilterOp",
    "Record",
    "RecordList",
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
    # web facade (dispatch adapter lives in core)
    "App",
    "Ctx",
    "Page",
    "Fragment",
    "Rendered",
    "Redirect",
    "redirect",
    "RouteDef",
    "Kind",
]
