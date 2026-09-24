"""Normalized inbound events — the vocabulary apps subscribe to.

A platform adapter (in core) translates a raw provider payload into an :class:`Event` with a stable
:class:`EventKind`; apps subscribe to kinds, never to a platform's wire format.
"""

from __future__ import annotations

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

    ``platform`` names the adapter the event came from (so emitted actions dispatch back to the same
    channel). ``group_id``/``sender_id`` are the platform's own opaque ids. ``raw`` is the original
    payload — available to handlers, never persisted by the core.
    """

    kind: EventKind
    platform: str
    group_id: str
    sender_id: str
    text: str = ""
    message_id: str = ""
    timestamp: datetime | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)
