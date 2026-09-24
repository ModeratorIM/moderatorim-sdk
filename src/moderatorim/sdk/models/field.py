"""Typed model fields — the ``Field`` declaration + the backend-neutral ``FieldType`` vocabulary.

A field carries enough type metadata for a relational backend to materialize a column and for a UI
layer to render an input. Types name intent (``REF``, ``LIST``, ``ENUM``), not a database's column
types — each backend maps them onto its own storage.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class FieldType(Enum):
    """The backend-neutral field-type vocabulary."""

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
    """A single typed field on a :class:`~moderatorim.sdk.models.Model`.

    Frozen: a field declaration is immutable. All invariants are checked in ``__post_init__`` so a
    malformed declaration fails loudly at import/boot, not at schema-materialization time.
    """

    type: FieldType
    required: bool = False
    unique: bool = False
    default: Any = None
    help: str = ""
    index: bool = False
    relation: str | None = None  # for REF: the target table name (app-namespaced)
    choices: tuple[str, ...] = ()  # for ENUM: the allowed string choices
    item_type: FieldType | None = None  # for LIST: the element type (a scalar FieldType)

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
