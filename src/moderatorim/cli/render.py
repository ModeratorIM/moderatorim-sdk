"""A tiny template renderer for the ``moderatorim`` CLI — no Jinja/cookiecutter dependency.

It walks a template directory under ``moderatorim/cli/templates/<kind>/`` and materialises it into a
destination directory, applying two rules:

* File bodies ending in ``.tmpl`` are rendered with ``str.format_map`` over the provided variables,
  and written WITHOUT the ``.tmpl`` suffix. Plain files are copied verbatim.
* A path segment equal to ``__name__`` is replaced by the ``name`` variable (used for the starter
  domain package directory).

Rendering never overwrites: if a destination file already exists the render is refused, so a
generator can never clobber the author's source.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Any


class RenderError(Exception):
    """A template could not be rendered (missing template, or a destination already exists)."""


def _templates_root() -> Path:
    """The on-disk root of the CLI's template tree (shipped as package data)."""
    return Path(str(resources.files("moderatorim.cli"))) / "templates"


def _subst(text: str, variables: dict[str, Any]) -> str:
    # Only the documented placeholders are substituted; a literal brace in a template must be
    # doubled ({{ }}) as usual for str.format. Missing keys raise, surfacing template bugs early.
    return text.format_map(variables)


def render_kind(kind: str, dest: Path, variables: dict[str, Any]) -> list[Path]:
    """Render the template set ``kind`` into ``dest``, returning the list of files written.

    ``variables`` supplies the substitution names (e.g. ``name``, ``Name``, ``app``, ``domain``).
    Raises :class:`RenderError` if the template set is missing or any destination file exists.
    """
    src_root = _templates_root() / kind
    if not src_root.is_dir():
        raise RenderError(f"no template set for kind {kind!r} (looked in {src_root})")

    written: list[Path] = []
    planned: list[tuple[Path, str | bytes]] = []
    for src in sorted(src_root.rglob("*")):
        if src.is_dir():
            continue
        rel = src.relative_to(src_root)
        # substitute __name__ path segments and {placeholder} names in path segments, and drop a
        # trailing .tmpl on the file name
        parts: list[str] = []
        for seg in rel.parts:
            if seg == "__name__":
                parts.append(str(variables["name"]))
            elif "{" in seg:
                parts.append(_subst(seg, variables))
            else:
                parts.append(seg)
        is_tmpl = parts[-1].endswith(".tmpl")
        if is_tmpl:
            parts[-1] = parts[-1][: -len(".tmpl")]
        out_path = dest.joinpath(*parts)
        if out_path.exists():
            raise RenderError(f"refusing to overwrite existing file: {out_path}")
        if is_tmpl:
            planned.append((out_path, _subst(src.read_text(encoding="utf-8"), variables)))
        else:
            planned.append((out_path, src.read_bytes()))

    # All destinations validated as non-existent above; now write.
    for out_path, content in planned:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            out_path.write_bytes(content)
        else:
            out_path.write_text(content, encoding="utf-8")
        written.append(out_path)
    return written
