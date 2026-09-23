"""The ``DataStore`` port — persistence behind a narrow interface.

A backend implements ``DataStore`` to provision tables and read/write records as plain dicts. The
query surface is deliberately **narrow**: a fixed set of filter operators (no arbitrary query
language), so every backend can implement it faithfully and no app can smuggle backend-specific
query semantics through the port.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from moderatorim.sdk.models import ResolvedSchema

# A record is a plain dict — the port never leaks an ORM row or a backend-native object.
Record = dict[str, Any]


class FilterOp(Enum):
    """The fixed, backend-neutral filter-operator set.

    Kept intentionally small: every backend must implement all of these, and nothing else is
    expressible through the port. Compound queries are built from a list of ``Filter`` clauses
    ANDed together (see :meth:`DataStore.list`).
    """

    EQ = "eq"  # equal
    NE = "ne"  # not equal
    LT = "lt"  # less than
    LTE = "lte"  # less than or equal
    GT = "gt"  # greater than
    GTE = "gte"  # greater than or equal
    IN = "in"  # value in a list
    CONTAINS = "contains"  # substring / membership (backend maps to LIKE / array-contains)


@dataclass(frozen=True, slots=True)
class Filter:
    """One filter clause: ``field <op> value``.

    A list of these is ANDed together by :meth:`DataStore.list`. This is the *only* way to
    express a query through the port — there is no raw-query escape hatch.
    """

    field: str
    op: FilterOp
    value: Any

    def __post_init__(self) -> None:
        if not self.field:
            raise ValueError("Filter.field must be a non-empty field name")
        if self.op is FilterOp.IN and not isinstance(self.value, list | tuple | set):
            raise ValueError("FilterOp.IN requires a list/tuple/set value")


# Type aliases used in method signatures below. Defined at module scope so annotations do not
# resolve the name ``list`` inside the DataStore class, where the ``list`` METHOD shadows the
# builtin under ``from __future__ import annotations`` (string-evaluated annotations).
FilterList = list[Filter]
RecordList = list[Record]


@runtime_checkable
class DataStore(Protocol):
    """Persistence port. Backends implement this; the core depends only on it.

    Records are plain dicts keyed by field name. Every model carries an implicit ``id`` (str)
    primary key and, when soft-delete is enabled, a ``deleted_at`` marker managed by the backend
    — a soft-deleted record is excluded from ``get``/``list``/``count``.
    """

    async def ensure_table(self, schema: ResolvedSchema) -> None:
        """Provision (create or migrate) the table for a resolved schema. Idempotent."""
        ...

    async def get(self, table: str, id: str) -> Record | None:
        """Fetch one record by primary key, or ``None`` if absent / soft-deleted."""
        ...

    async def list(
        self,
        table: str,
        filters: FilterList | None = None,
        *,
        limit: int | None = None,
        offset: int = 0,
        order_by: str | None = None,
        descending: bool = False,
    ) -> RecordList:
        """Return records matching ALL ``filters`` (ANDed), with optional paging/ordering."""
        ...

    async def create(self, table: str, data: Record) -> Record:
        """Insert a record. If ``id`` is absent the backend assigns one. Returns the stored row."""
        ...

    async def update(self, table: str, id: str, data: Record) -> Record:
        """Partially update a record by id (only the supplied fields). Returns the stored row."""
        ...

    async def delete(self, table: str, id: str) -> None:
        """Delete by id. Soft delete (set ``deleted_at``) when the schema enables it, else hard."""
        ...

    async def count(self, table: str, filters: FilterList | None = None) -> int:
        """Count records matching ALL ``filters`` (ANDed)."""
        ...
