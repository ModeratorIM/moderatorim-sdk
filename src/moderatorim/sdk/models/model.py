"""The ``Model`` base — an app declares a model by subclassing it, setting ``table`` and ``fields``.

A model is a *declaration*, not an ORM row: it describes a schema. The core provisions it through
the ``DataStore`` port; table names are app-namespaced to prevent collisions between apps.
"""

from __future__ import annotations

from moderatorim.sdk.models.field import Field

# Every model carries an implicit primary key and soft-delete marker; backends honor these.
ID_FIELD = "id"
SOFT_DELETE_FIELD = "deleted_at"


class Model:
    """Base class for a declared model.

    Subclasses set:
      * ``table`` — the FULL physical table name, MANDATORY and prefixed with the owning unit's
        name (``<unit>_<name>``, lowercase snake_case, e.g. ``admin_post``). You DECLARE the full
        name — the framework does NOT generate or rewrite it, so the name you write is the name in
        the database (a raw query or ``ref`` never diverges from the declaration). Core validates at
        boot that the prefix matches the owning unit and FAILS LOUDLY otherwise.
      * ``fields`` — mapping of field name -> :class:`~moderatorim.sdk.models.field.Field`.
      * ``soft_delete`` — if True (default), ``DataStore.delete`` is a soft delete.

    Field names ``id`` and ``deleted_at`` are reserved (managed by the core/backend).
    """

    table: str
    fields: dict[str, Field] = {}
    soft_delete: bool = True

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        # An abstract intermediate subclass may omit `table`; concrete models must set it.
        table = getattr(cls, "table", None)
        if table is None:
            return
        _validate_table_name(table)
        _validate_fields(cls.fields)


def _validate_table_name(table: str) -> None:
    if not table:
        raise ValueError("Model.table must be a non-empty string")
    if not table.islower() or " " in table:
        raise ValueError(f"Model.table must be lowercase snake_case: {table!r}")
    if "_" not in table:
        raise ValueError(f"Model.table must be app-namespaced as '<app>_<name>' (got {table!r})")


def _validate_fields(fields: dict[str, Field]) -> None:
    for name, f in fields.items():
        if name in (ID_FIELD, SOFT_DELETE_FIELD):
            raise ValueError(f"field name {name!r} is reserved by the core")
        if not isinstance(f, Field):
            raise TypeError(f"field {name!r} must be a Field, got {type(f).__name__}")
