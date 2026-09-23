"""Facade unit tests for the SDK web surface (registration only — dispatch is core's adapter)."""

from __future__ import annotations

from moderatorim.sdk import App, Ctx, Fragment, Kind, Page, Redirect, Rendered, redirect


def test_page_action_post_record_routedefs() -> None:
    app = App()

    @app.page("/hello", title="Hello", nav="Home")
    def hello(ctx: Ctx) -> Page:
        return Page(title="Hello", content=["hi"])

    @app.action("/go", permission="a.b")
    def go(ctx: Ctx) -> Redirect:
        return redirect("/dest")

    @app.post("/chip")
    def chip(ctx: Ctx) -> Fragment:
        return Fragment("<span>ok</span>")

    routes = app.routes
    assert [r.path for r in routes] == ["/hello", "/go", "/chip"]
    assert routes[0].kind is Kind.PAGE and routes[0].methods == ("GET",) and routes[0].nav == "Home"
    assert routes[1].kind is Kind.ACTION and routes[1].permission == "a.b"
    assert routes[2].kind is Kind.POST and routes[2].methods == ("POST",)


def test_action_custom_methods() -> None:
    app = App()

    @app.action("/x", methods=("POST", "DELETE"))
    def x(ctx: Ctx) -> Redirect:
        return redirect("/")

    assert app.routes[0].methods == ("POST", "DELETE")


def test_nav_routes_only_nav_declared() -> None:
    app = App()

    @app.page("/dash", title="Dash", nav="Dashboard")
    def dash(ctx: Ctx) -> Page:
        return Page(title="Dash", content=[])

    @app.page("/hidden", title="Hidden")
    def hidden(ctx: Ctx) -> Page:
        return Page(title="Hidden", content=[])

    navs = app.nav_routes
    assert len(navs) == 1 and navs[0].nav == "Dashboard" and navs[0].path == "/dash"


def test_primitives() -> None:
    assert redirect("/x").url == "/x"
    assert redirect("/x", replace=True).replace is True
    assert Page(title="T", content=["b"], permission="p.q.read").permission == "p.q.read"
    assert Rendered("body", status=404).status == 404
    assert Fragment("<i>").html == "<i>"


def test_ctx_cookie_and_helpers() -> None:
    ctx = Ctx(config=object(), request=object())
    ctx.set_session("tok")
    assert ctx._set_session == "tok"
    ctx.clear_session()
    assert ctx._clear_session is True and ctx._set_session is None
    ctx.set_cookie("mim_setup_ok", "k", path="/setup", max_age=3600)
    assert ctx._extra_cookies == [("mim_setup_ok", "k", "/setup", 3600)]
    assert ctx.can("anything") is False  # default predicate denies
