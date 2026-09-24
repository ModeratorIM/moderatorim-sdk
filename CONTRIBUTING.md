# Contributing to moderatorim-sdk

Thanks for your interest! `moderatorim-sdk` is the **contract kernel** of the ModeratorIM project —
the small, dependency-free package that both the ModeratorIM core runtime and every ModeratorIM app
build against (`from moderatorim.sdk import Manifest, App, Ctx, Page, Model, ...`).

> **Status:** early development, pre-1.0. The contract surface is still moving — expect breaking
> changes between `0.0.x` versions until it stabilizes.

## Ground rules

- Be respectful — this project follows a [Code of Conduct](CODE_OF_CONDUCT.md).
- Report security issues **privately**, never in a public issue — see [SECURITY.md](SECURITY.md).

## What belongs here (and what does NOT)

This package is **contracts only** — declarations, no runtime:

- ✅ Data-model declarations (`Model`, `Field`, `Extends`, `ResolvedSchema`).
- ✅ The `DataStore` port, the event bus (`Event`/`Action`/`EventBus`), the `Manifest`, and the web
  facade (`App`/`Ctx`/`Page`).
- ❌ **No runtime, no I/O, no heavy dependencies.** No Starlette, no database driver, no network.
  The *implementation* of these contracts lives in the core runtime, not here. A change that needs
  a runtime dependency belongs in core.

Keeping the SDK dependency-free is the point: an app installs `moderatorim-sdk` alone, without
pulling in the core runtime.

## Development setup

Requirements: **Python 3.11+**.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
```

### Checks (must pass before a PR)

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

### Working across core + SDK

Core depends on this package. When a change here affects core, develop them together: in the core
checkout, install this SDK editable (`pip install -e ../moderatorim-sdk`), and run **both** test
suites. A contract change usually needs a matching change in core's implementation — land the SDK
change first (this repo), then update core.

## Workflow

- Branch from `main`; open a pull request. `main` is protected — no direct pushes.
- Keep the public API in `moderatorim/sdk/__init__.py` curated and stable; adding a name is cheap,
  renaming/removing one is a breaking change (call it out in the PR and the CHANGELOG).
- One logical change per PR. Update [CHANGELOG.md](CHANGELOG.md) for any public-surface change.

## Licensing / CLA

ModeratorIM is **dual-licensed** (AGPL-3.0 + a commercial license). Contributors are asked to sign
a lightweight **CLA** before their first contribution is merged, so the project can keep both
options open while the code stays free and open.

<!-- TODO: link the CLA document / signing flow before the first public release. -->
