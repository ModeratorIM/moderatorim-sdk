"""The event bus: subscribe + publish/fan-out.

Apps register async handlers for an :class:`~moderatorim.sdk.bus.events.EventKind`. Publishing an
event fans it out to every subscribed handler and collects the
:class:`~moderatorim.sdk.bus.actions.Action`s they emit. The bus decides nothing — it only carries
events out and actions back.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Awaitable, Callable

from moderatorim.sdk.bus.actions import Action
from moderatorim.sdk.bus.events import Event, EventKind

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
