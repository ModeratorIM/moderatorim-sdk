"""The ``Component`` base — the contract every UI component follows.

A component is a **class** that renders itself to safe HTML in Python (no template engine). The
base gives every component a uniform shape and, crucially, lets components **compose without
importing each other**: a component instance passed as a child renders via ``__html__`` (which
the ``tag`` primitive honors), so ``Card(Button("Save"))`` works with no lateral import.

This shared contract is the ONE thing every component depends on (alongside the ``html``
primitive) — the isolation rule is: a component imports ``component`` + ``html`` (+ ``validation``
where relevant) and NEVER another component.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from moderatorim.ui.html import Raw


class Component(ABC):
    """Base class for a UI component. Subclasses implement :meth:`render`."""

    @abstractmethod
    def render(self) -> Raw:
        """Return this component's safe HTML."""
        ...

    def __html__(self) -> str:
        """Compose as a child of another component (the ``tag`` primitive calls this)."""
        return str(self.render())

    def __str__(self) -> str:
        return str(self.render())
