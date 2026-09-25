"""The ``moderatorim`` command-line tool — scaffolds ModeratorIM units and their components.

This module lives at ``moderatorim.cli`` (a sibling of ``moderatorim.sdk``, SDK-owned by
convention) and is exposed as the ``moderatorim`` console script. It is a thin ``argparse``
dispatcher; the templating work lives in :mod:`moderatorim.cli.render`.

v1 implements ``create app`` (a create-container action that runs in ANY directory). The
domain-first ``generate`` family (operate-in-app) is a fast-follow.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from moderatorim.cli.render import RenderError, render_kind

# A unit module name: lowercase, starts with a letter, letters/digits/underscore — matches the
# Manifest.name rule (lowercase, no spaces) and is import-safe as a package name.
_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _title_from(name: str) -> str:
    """A default human title from a module name: 'my_product' -> 'My Product'."""
    return " ".join(part.capitalize() for part in name.split("_"))


def _create_app(args: argparse.Namespace) -> int:
    name: str = args.name
    if not _NAME_RE.match(name):
        print(
            f"error: {name!r} is not a valid module name — use lowercase letters, digits and "
            "underscores, starting with a letter (e.g. 'my_product').",
            file=sys.stderr,
        )
        return 2

    dest = Path.cwd() / name
    if dest.exists():
        print(f"error: {dest} already exists — refusing to overwrite.", file=sys.stderr)
        return 2

    display_name = args.display_name or _title_from(name)
    description = args.description or f"The {display_name} ModeratorIM app."
    variables = {
        "name": name,
        "Name": name[:1].upper() + name[1:],
        "display_name": display_name,
        "description": description,
        "version": args.version,
    }
    try:
        written = render_kind("app", dest, variables)
    except RenderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Created app {name!r} at {dest} ({len(written)} files).")
    print(f"  Next: cd {name} && moderatorim generate model <domain>")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="moderatorim", description="ModeratorIM app scaffolding CLI."
    )
    sub = parser.add_subparsers(dest="verb", metavar="<verb>")

    create = sub.add_parser("create", help="Create a new unit (app / backend / platform).")
    create_sub = create.add_subparsers(dest="kind", metavar="<kind>")

    app = create_sub.add_parser("app", help="Scaffold a new app in the current directory.")
    app.add_argument("name", help="Module name (lowercase, e.g. 'my_product').")
    app.add_argument(
        "--display-name",
        "--name",
        dest="display_name",
        default="",
        help="Human-facing title (Manifest.display_name). Defaults to a title-cased module name.",
    )
    app.add_argument(
        "--description",
        default="",
        help="One-line description (goes in the generated README, not the manifest).",
    )
    app.add_argument("--version", default="0.0.0", help="Initial Manifest.version (default 0.0.0).")
    app.set_defaults(func=_create_app)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help(sys.stderr)
        return 2
    return int(func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
