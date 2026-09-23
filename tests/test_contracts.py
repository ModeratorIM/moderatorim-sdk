"""Contract unit tests for the moved SDK modules (models, datastore, bus, manifest)."""

from __future__ import annotations

import asyncio

import pytest

from moderatorim.sdk import (
    Action,
    ActionKind,
    DataStore,
    Event,
    EventBus,
    EventKind,
    Extends,
    Field,
    FieldType,
    Filter,
    FilterOp,
    Manifest,
    Model,
    NavEntry,
    ResolvedSchema,
    UnitType,
    enum,
    list_of,
    ref,
)


# -- models ----------------------------------------------------------------------
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
    from moderatorim.sdk import ResolvedColumn

    s = ResolvedSchema(
        table="app_thing",
        columns=(ResolvedColumn("id", Field(FieldType.STR)),),
        soft_delete=False,
    )
    assert s.column_names() == ("id",)


# -- datastore port --------------------------------------------------------------
def test_filter_in_requires_sequence() -> None:
    assert Filter("x", FilterOp.EQ, 1).op is FilterOp.EQ
    with pytest.raises(ValueError, match="IN requires"):
        Filter("x", FilterOp.IN, 1)


def test_datastore_is_runtime_checkable_protocol() -> None:
    class Fake:
        async def ensure_table(self, schema: object) -> None: ...
        async def get(self, table: str, id: str) -> object: ...
        async def list(self, table: str, filters: object = None, **kw: object) -> list: ...  # type: ignore[type-arg]
        async def create(self, table: str, data: object) -> object: ...
        async def update(self, table: str, id: str, data: object) -> object: ...
        async def delete(self, table: str, id: str) -> None: ...
        async def count(self, table: str, filters: object = None) -> int: ...

    assert isinstance(Fake(), DataStore)


# -- bus -------------------------------------------------------------------------
def test_action_requires_group_id() -> None:
    assert Action(ActionKind.SEND_MESSAGE, group_id="g", text="hi").text == "hi"
    with pytest.raises(ValueError, match="group_id"):
        Action(ActionKind.SEND_MESSAGE, group_id="")


def test_bus_fans_out_and_collects_actions() -> None:
    bus = EventBus()

    async def handler(ev: Event) -> list[Action]:
        return [Action(ActionKind.SEND_MESSAGE, group_id=ev.group_id, text="ack")]

    bus.subscribe(EventKind.MESSAGE_RECEIVED, handler)
    assert bus.subscriber_count(EventKind.MESSAGE_RECEIVED) == 1
    ev = Event(kind=EventKind.MESSAGE_RECEIVED, platform="x", group_id="g", sender_id="s")
    actions = asyncio.run(bus.publish(ev))
    assert len(actions) == 1 and actions[0].text == "ack"


# -- manifest --------------------------------------------------------------------
def test_manifest_basics_and_routes_hook() -> None:
    m = Manifest(
        name="widget",
        type=UnitType.APP,
        register=lambda core: None,
        nav=(NavEntry("Widget", "/widget", "star"),),
        routes=lambda app: None,
    )
    assert m.title == "Widget" and m.routes is not None
    with pytest.raises(TypeError, match="routes must be callable"):
        Manifest(name="bad", type=UnitType.APP, register=lambda c: None, routes=1)  # type: ignore[arg-type]


def test_manifest_name_validation() -> None:
    with pytest.raises(ValueError, match="lowercase"):
        Manifest(name="Widget", type=UnitType.APP, register=lambda c: None)
