"""Core actions — what an app's handler asks the platform to do in response to an event.

The action vocabulary is fixed and platform-neutral; a core adapter maps each kind onto its own API.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


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
