"""The event bus contract: normalized inbound :class:`Event`s, the :class:`Action`s a handler
emits in response, and the :class:`EventBus` that carries them.

A platform adapter (in core) translates a raw provider payload into an :class:`Event` with a
stable :class:`EventKind`; apps subscribe to kinds, never to a platform's wire format, and return
:class:`Action`s the dispatcher maps back onto the originating platform. The bus itself decides
nothing — it only carries events out and actions back.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EventKind(Enum):
    """The normalized inbound event kinds apps can subscribe to."""

    MESSAGE_RECEIVED = "message_received"
    MEMBER_JOINED = "member_joined"
    MEMBER_LEFT = "member_left"
    JOIN_REQUESTED = "join_requested"


@dataclass(frozen=True, slots=True)
class Event:
    """A normalized inbound event.

    ``platform`` names the adapter the event came from (so emitted actions dispatch back to the
    same channel). ``group_id``/``sender_id`` are the platform's own opaque ids. ``raw`` is the
    original payload — available to handlers, never persisted by the core.
    """

    kind: EventKind
    platform: str
    group_id: str
    sender_id: str
    text: str = ""
    message_id: str = ""
    timestamp: datetime | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)


class ActionKind(Enum):
    """The fixed, platform-neutral moderation/communication action vocabulary."""

    SEND_MESSAGE = "send_message"  # post a message to the group
    DELETE_MESSAGE = "delete_message"  # delete a specific message
    WARN_MEMBER = "warn_member"  # warn a member (a directed message + a recorded warning)
    MUTE_MEMBER = "mute_member"
    REMOVE_MEMBER = "remove_member"
    APPROVE_JOIN = "approve_join"
    DENY_JOIN = "deny_join"


@dataclass(frozen=True, slots=True)
class Action:
    """One action an app wants performed on ``group_id`` (optionally targeting ``target_id``).

    ``text`` carries the message body for SEND_MESSAGE / WARN_MEMBER; ``message_id`` targets a
    specific message for DELETE_MESSAGE; ``target_id`` names the member for member-scoped kinds.
    """

    kind: ActionKind
    group_id: str
    text: str = ""
    target_id: str = ""
    message_id: str = ""

    def __post_init__(self) -> None:
        if not self.group_id:
            raise ValueError("Action.group_id is required")


# A handler takes an Event and returns the Actions it wants performed (possibly none).
Handler = Callable[[Event], Awaitable[list[Action]]]


class EventBus:
    """In-process publish/subscribe over :class:`EventKind`."""

    def __init__(self) -> None:
        self._handlers: dict[EventKind, list[Handler]] = defaultdict(list)

    def subscribe(self, kind: EventKind, handler: Handler) -> None:
        """Register ``handler`` for ``kind``. A handler may subscribe to several kinds."""
        self._handlers[kind].append(handler)

    def subscriber_count(self, kind: EventKind) -> int:
        return len(self._handlers.get(kind, []))

    async def publish(self, event: Event) -> list[Action]:
        """Fan ``event`` out to all handlers for its kind; return their collected actions.

        Handlers run concurrently. If any handler raises, the others still complete and their
        actions are discarded only for the failed handler; the first exception is re-raised after
        all have settled.
        """
        handlers = list(self._handlers.get(event.kind, []))
        if not handlers:
            return []
        results = await asyncio.gather(*(h(event) for h in handlers), return_exceptions=True)
        actions: list[Action] = []
        first_error: BaseException | None = None
        for result in results:
            if isinstance(result, BaseException):
                first_error = first_error or result
                continue
            actions.extend(result)
        if first_error is not None:
            raise first_error
        return actions
