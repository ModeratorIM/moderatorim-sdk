"""Tests for the generic ``moderatorim.ui.Header`` app bar."""

from __future__ import annotations

from moderatorim.ui import Button, Header, tag


def test_header_title_and_actions() -> None:
    html = str(Header("Members", actions=[Button("Invite", icon="add")]))
    assert "<header" in html and "<nav" in html
    assert "Members" in html and "max" in html  # title cell pushes actions right
    assert "Invite" in html  # action rendered
    # generic — no ModeratorIM chrome classes/hooks
    assert "mim-" not in html


def test_header_leading_slot() -> None:
    html = str(Header("Title", leading=tag("button", tag("i", "menu"))))
    assert "<i>menu</i>" in html
    # leading comes before the title
    assert html.index("menu") < html.index("Title")


def test_header_bare_title_only() -> None:
    html = str(Header("Just a title"))
    assert "<header" in html and "Just a title" in html
    assert "mim-" not in html
