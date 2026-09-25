"""Register a generated model into a unit's ``manifest.py`` — the ONE existing-file edit the CLI
makes (design §5/§6: strictly additive — an import line + one ``models=`` entry, never a rewrite of
existing bodies).

The manifest calls ``Manifest(...)`` at module level. Registration:

* adds ``from <domain>.model import <Domain>`` after the last existing ``from`` import, and
* adds ``<Domain>`` to the ``models=(...)`` tuple — appending if the kwarg exists, else inserting a
  fresh ``models=(<Domain>,)`` kwarg just before the closing ``)`` of the ``Manifest(`` call.

Deliberately conservative: if the manifest does not match the expected shape the edit is refused
(``ManifestEditError``) rather than risk corrupting the author's source.
"""

from __future__ import annotations

import re
from pathlib import Path


class ManifestEditError(Exception):
    """The manifest could not be edited safely (unexpected shape, or already registered)."""


def register_model(manifest_path: Path, app: str, domain: str, model_class: str) -> None:
    """Add an import for ``<app>.<domain>.model.<model_class>`` and register it in ``models=(...)``.

    The import is APP-QUALIFIED (``from {app}.{domain}.model import {Model}``) to match how units
    are loaded — the grouping dir is on ``sys.path`` and the app is imported by its package name, so
    intra-app imports are package-qualified (as in the reference admin app)."""
    src = manifest_path.read_text(encoding="utf-8")
    import_line = f"from {app}.{domain}.model import {model_class}"

    if model_class in src and import_line in src:
        raise ManifestEditError(f"{model_class} already registered in {manifest_path.name}")

    lines = src.splitlines(keepends=True)

    # 1. Insert the import after the last top-level `from `/`import ` line.
    last_import = -1
    for i, line in enumerate(lines):
        if line.startswith(("from ", "import ")):
            last_import = i
    if last_import < 0:
        raise ManifestEditError("no import block found to attach the model import after")
    lines.insert(last_import + 1, import_line + "\n")
    src = "".join(lines)

    # 2. Register in models=(...). Append to an existing tuple, else insert the kwarg.
    models_kwarg = re.search(r"models\s*=\s*\(([^)]*)\)", src)
    if models_kwarg:
        inner = models_kwarg.group(1).strip()
        if inner and not inner.endswith(","):
            inner += ","
        new_inner = f"{inner} {model_class}," if inner else f"{model_class},"
        src = src[: models_kwarg.start()] + f"models=({new_inner})" + src[models_kwarg.end() :]
    else:
        # Insert `models=(<Model>,)` as a new kwarg just before the closing ) of Manifest(...).
        call = re.search(r"manifest\s*=\s*Manifest\(", src)
        if call is None:
            raise ManifestEditError("no `manifest = Manifest(` call found to register the model in")
        # find the matching close paren for that call
        depth = 0
        close = None
        for i in range(call.end() - 1, len(src)):
            if src[i] == "(":
                depth += 1
            elif src[i] == ")":
                depth -= 1
                if depth == 0:
                    close = i
                    break
        if close is None:
            raise ManifestEditError("unbalanced parentheses in the Manifest(...) call")
        # insert before the closing paren, matching the call's indentation of kwargs
        insertion = f"    models=({model_class},),\n"
        # ensure we sit on its own line: back up over trailing whitespace/newline before ')'
        head = src[:close].rstrip()
        if not head.endswith(","):
            head += ","
        src = head + "\n" + insertion + src[close:]

    manifest_path.write_text(src, encoding="utf-8")
