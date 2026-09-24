"""Contract tests for the models domain (Field/FieldType, Model, Extends, ResolvedSchema)."""

from __future__ import annotations

import pytest

from moderatorim.sdk import (
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


def test_field_ref_requires_relation() -> None:
    with pytest.raises(ValueError, match="REF field requires"):
        Field(FieldType.REF)
    assert ref("contact_contact").relation == "contact_contact"


def test_field_enum_and_list_invariants() -> None:
    assert enum("a", "b").choices == ("a", "b")
    with pytest.raises(ValueError, match="ENUM field requires"):
        Field(FieldType.ENUM)
    assert list_of(FieldType.STR).item_type is FieldType.STR
    with pytest.raises(ValueError, match="scalar type"):
        Field(FieldType.LIST, item_type=FieldType.REF)


def test_model_table_must_be_namespaced() -> None:
    with pytest.raises(ValueError, match="app-namespaced"):

        class Bad(Model):
            table = "contacts"  # no underscore namespace

    class Good(Model):
        table = "contact_contact"
        fields = {"name": Field(FieldType.STR)}

    assert Good.table == "contact_contact"


def test_model_reserved_field_rejected() -> None:
    with pytest.raises(ValueError, match="reserved"):

        class Bad(Model):
            table = "app_thing"
            fields = {"id": Field(FieldType.STR)}


def test_extends_validates() -> None:
    e = Extends(base="core.auth.User", delegate_to="contact_contact", link="contact_id")
    assert e.link == "contact_id"
    with pytest.raises(ValueError, match="link"):
        Extends(base="x", delegate_to="y", link="not an identifier")


def test_resolved_schema_column_names() -> None:
    s = ResolvedSchema(
        table="app_thing",
        columns=(ResolvedColumn("id", Field(FieldType.STR)),),
        soft_delete=False,
    )
    assert s.column_names() == ("id",)
