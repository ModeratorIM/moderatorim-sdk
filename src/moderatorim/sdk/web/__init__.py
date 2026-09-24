"""The routing-facade contract domain: the App registration surface + the primitives handlers
return/receive. The dispatch adapter that renders these lives in core."""

from moderatorim.sdk.web.app import App, Kind, RouteDef
from moderatorim.sdk.web.primitives import Ctx, Fragment, Page, Redirect, Rendered, redirect

__all__ = ["App", "Kind", "RouteDef", "Ctx", "Fragment", "Page", "Redirect", "Rendered", "redirect"]
