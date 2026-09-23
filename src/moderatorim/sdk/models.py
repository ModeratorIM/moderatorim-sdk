"""The ModeratorIM data-model contract: :class:`Field`/:class:`FieldType`, the :class:`Model`
base, and the :class:`Extends` inheritance link.

A model is a *declaration*, not an ORM row: it describes a schema. The core provisions it through
the ``DataStore`` port and reads/writes records as plain dicts. Types are backend-neutral — they
name intent (``REF``, ``LIST``, ``ENUM``), and each backend maps them onto its own storage.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

# Every model carries an implicit primary key and soft-delete marker; backends honor these.
ID_FIELD = "id"
SOFT_DELETE_FIELD = "deleted_at"


class FieldType(Enum):
    """The backend-neutral field-type vocabulary.

    Backends map each onto their own storage (SQL column type / an API attribute / etc.).
    """

    STR = "str"  # short string (indexable, length-bounded by the backend default)
    TEXT = "text"  # long / unbounded text
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    DATETIME = "datetime"
    DATE = "date"
    JSON = "json"  # arbitrary JSON blob
    ENUM = "enum"  # one of a fixed set of string choices (see Field.choices)
    REF = "ref"  # reference to another model (see Field.relation -> table name)
    LIST = "list"  # a list of scalars (e.g. list[str] for phones/tags)


@dataclass(frozen=True, slots=True)
class Field:
    """A single typed field on a :class:`Model`.

    Frozen: a field declaration is immutable once made. All construction-time invariants are
    checked in ``__post_init__`` so a malformed declaration fails loudly at import/boot, not at
    schema-materialization time.
    """

    type: FieldType
    required: bool = False
    unique: bool = False
    default: Any = None
    help: str = ""
    index: bool = False
    # For REF: the target table name (app-namespaced), e.g. "contact_contact".
    relation: str | None = None
    # For ENUM: the allowed string choices.
    choices: tuple[str, ...] = ()
    # For LIST: the element type (a scalar FieldType; not REF/LIST/JSON).
    item_type: FieldType | None = None

    def __post_init__(self) -> None:
        if self.type is FieldType.REF and not self.relation:
            raise ValueError("REF field requires `relation` (the target table name)")
        if self.type is not FieldType.REF and self.relation is not None:
            raise ValueError("`relation` is only valid on a REF field")

        if self.type is FieldType.ENUM and not self.choices:
            raise ValueError("ENUM field requires non-empty `choices`")
        if self.type is not FieldType.ENUM and self.choices:
            raise ValueError("`choices` is only valid on an ENUM field")

        if self.type is FieldType.LIST:
            if self.item_type is None:
                raise ValueError("LIST field requires `item_type`")
            if self.item_type in (FieldType.LIST, FieldType.REF, FieldType.JSON):
                raise ValueError("LIST `item_type` must be a scalar type")
        elif self.item_type is not None:
            raise ValueError("`item_type` is only valid on a LIST field")


def ref(table: str, *, required: bool = False, index: bool = True, help: str = "") -> Field:
    """Convenience constructor for a REF field (relations are indexed by default)."""
    return Field(FieldType.REF, relation=table, required=required, index=index, help=help)


def enum(*choices: str, required: bool = False, default: Any = None, help: str = "") -> Field:
    """Convenience constructor for an ENUM field."""
    return Field(
        FieldType.ENUM, choices=tuple(choices), required=required, default=default, help=help
    )


def list_of(item: FieldType, *, help: str = "") -> Field:
    """Convenience constructor for a LIST field of a scalar ``item`` type."""
    return Field(FieldType.LIST, item_type=item, default=(), help=help)


class Model:
    """Base class for a declared model.

    Subclasses set:
      * ``table`` — app-namespaced table name (``<app>_<name>``), lowercase snake_case.
      * ``fields`` — mapping of field name -> :class:`Field`.
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


@dataclass(frozen=True, slots=True)
class ResolvedColumn:
    """One column in a resolved schema — a field plus its final name."""

    name: str
    field: Field


@dataclass(frozen=True, slots=True)
class ResolvedSchema:
    """The final, materializable schema a backend provisions.

    Carries the table name, the ordered columns (including the implicit primary key and, when
    ``soft_delete`` is set, the soft-delete marker), and the soft_delete flag. A backend maps
    each column's :class:`FieldType` onto its own storage. The core computes this (its merge of a
    base model + any ``Extends`` links) before any backend call; the backend only receives the
    result through the ``DataStore`` port.
    """

    table: str
    columns: tuple[ResolvedColumn, ...]
    soft_delete: bool

    def column_names(self) -> tuple[str, ...]:
        return tuple(c.name for c in self.columns)


@dataclass(frozen=True, slots=True)
class Extends:
    """A delegation-inheritance link declared in an app's manifest.

    Semantics: the ``base`` model gains a REF column named ``link`` pointing at the
    ``delegate_to`` table. The extending app owns ``delegate_to`` (its rich record); the base
    keeps its own columns and simply carries the foreign key. The actual merge into one
    materializable schema is done by the core before any backend call.

    Example — ``contact`` extends ``core.auth.User``::

        Extends(base="core.auth.User", delegate_to="contact_contact", link="contact_id")
    """

    base: str  # dotted model id of the base, e.g. "core.auth.User"
    delegate_to: str  # table holding the extended record, e.g. "contact_contact"
    link: str  # FK field name added to the base table, e.g. "contact_id"

    def __post_init__(self) -> None:
        if not self.base:
            raise ValueError("Extends.base is required (dotted model id of the base)")
        if not self.delegate_to:
            raise ValueError("Extends.delegate_to is required (target table name)")
        if not self.link:
            raise ValueError("Extends.link is required (FK field name on the base)")
        if not self.link.isidentifier():
            raise ValueError(f"Extends.link must be a valid identifier: {self.link!r}")
