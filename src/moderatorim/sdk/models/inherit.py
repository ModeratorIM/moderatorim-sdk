"""Declared model inheritance — the ``Extends`` delegation link an app declares in its manifest."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Extends:
    """A delegation-inheritance link declared in an app's manifest.

    Semantics: the ``base`` model gains a REF column named ``link`` pointing at the ``delegate_to``
    table. The extending app owns ``delegate_to`` (its rich record); the base keeps its own columns
    and carries the foreign key. The actual merge into one materializable schema is done by the core
    before any backend call.

    Example — ``contact`` extends ``core.auth.User``::

        Extends(base="core.auth.User", delegate_to="contact_contact", link="contact_id")
    """

    base: str  # dotted model id of the base, e.g. "core.auth.User"
    delegate_to: str  # table holding the extended record, e.g. "contact_contact"
    link: str  # FK field name added to the base table, e.g. "contact_id"

    def __post_init__(self) -> None:
        if not self.base:
            raise ValueError("Extends.base is required (dotted model id of the base)")
        if not self.delegate_to:
            raise ValueError("Extends.delegate_to is required (target table name)")
        if not self.link:
            raise ValueError("Extends.link is required (FK field name on the base)")
        if not self.link.isidentifier():
            raise ValueError(f"Extends.link must be a valid identifier: {self.link!r}")
