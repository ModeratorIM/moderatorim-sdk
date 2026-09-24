"""Contract tests for the bus domain (Event/Action + EventBus fan-out)."""

from __future__ import annotations

import asyncio

import pytest

from moderatorim.sdk import Action, ActionKind, Event, EventBus, EventKind


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
