"""The data-model contract domain: fields, the Model base, inheritance, and the resolved schema."""

from moderatorim.sdk.models.field import Field, FieldType, enum, list_of, ref
from moderatorim.sdk.models.inherit import Extends
from moderatorim.sdk.models.model import ID_FIELD, SOFT_DELETE_FIELD, Model
from moderatorim.sdk.models.schema import ResolvedColumn, ResolvedSchema

__all__ = [
    "Field",
    "FieldType",
    "ref",
    "enum",
    "list_of",
    "Model",
    "ID_FIELD",
    "SOFT_DELETE_FIELD",
    "Extends",
    "ResolvedColumn",
    "ResolvedSchema",
]
