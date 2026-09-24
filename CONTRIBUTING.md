# Contributing to moderatorim-sdk

Thanks for your interest! `moderatorim-sdk` is the **contract kernel** of the ModeratorIM project —
the small, dependency-free package that both the ModeratorIM core runtime and every ModeratorIM app
build against (`from moderatorim.sdk import Manifest, App, Ctx, Page, Model, ...`).

> **Status:** early development, pre-1.0. The contract surface is still moving — expect breaking
> changes between `0.0.x` versions until it stabilizes.

## Ground rules

- Be respectful — this project follows a [Code of Conduct](CODE_OF_CONDUCT.md).
- Report security issues **privately**, never in a public issue — see [SECURITY.md](SECURITY.md).

## Filing issues

Use the **issue templates** (Bug report / Feature request) — blank issues are disabled. Guidelines:

- **One concern per issue.** A bug and a feature are two issues.
- **Label by type:** `bug`, `enhancement` (a feature/contract addition), `documentation`, `chore`.
  Add **`breaking`** when the change removes/renames/retypes a public thing or tightens validation —
  that label signals a MAJOR (pre-1.0: MINOR) bump per [VERSIONING.md](VERSIONING.md).
- **Milestones = target releases.** Open issues are grouped by the release they'll ship in
  (`0.1.0`, later `0.2.0`, …). The **`1.0.0`** milestone is the *stability gate* — file
  "must-be-true-before-the-API-is-stable" issues there, not a fixed next-step.
- **Security** → never a public issue; use the private channel in [SECURITY.md](SECURITY.md).
- **Questions** → the project discussions, not an issue.

> Issues are the **public tracker** (bugs, requests, coordination). Detailed internal design lives
> in the maintainers' own planning docs, not in issues — keep issues focused and outward-facing.

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
- One logical change per PR. Update [CHANGELOG.md](CHANGELOG.md) for any public-surface change. Version bumps + the release process are in [RELEASING.md](RELEASING.md); what the versions promise consumers is in [VERSIONING.md](VERSIONING.md).

## Licensing / CLA

ModeratorIM is **dual-licensed** (AGPL-3.0 + a commercial license). Contributors are asked to sign
a lightweight **CLA** before their first contribution is merged, so the project can keep both
options open while the code stays free and open.

<!-- TODO: link the CLA document / signing flow before the first public release. -->
