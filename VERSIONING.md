# Versioning

`moderatorim-sdk` is the **contract kernel** the ModeratorIM core runtime and every ModeratorIM app
build against. Its version number IS a compatibility promise, so we version it deliberately.

## Scheme: Semantic Versioning

We follow [SemVer 2.0](https://semver.org): **`MAJOR.MINOR.PATCH`**. For this package the "public
API" is precisely:

- every name exported from `moderatorim.sdk` (the curated `__all__` in `src/moderatorim/sdk/__init__.py`), and
- the **shape** of each of those contracts — a dataclass's fields and their types, a `Protocol`'s
  method signatures (`DataStore`), an enum's members (`FieldType`/`EventKind`/`ActionKind`),
  `Ctx`'s attributes, and the accepted-input rules enforced in `__post_init__`/validation.

| Bump | Meaning for the contract |
| --- | --- |
| **MAJOR** | A **breaking** change: remove/rename a public name; remove or retype a dataclass field; change a `DataStore` signature; change `Ctx`'s shape; tighten validation so a previously-valid declaration now fails. Anything that could make a working app stop importing or running. |
| **MINOR** | A **backward-compatible addition**: a new public name; a new optional field with a default; a new enum member; a new optional parameter. Existing apps keep working untouched. |
| **PATCH** | **No surface change**: docs, an internal refactor, a bug fix that does not change accepted inputs, packaging metadata. |

### Pre-1.0 (where we are)

While the version is `0.y.z` the contract is **not yet stable**. We still bump meaningfully:

- a **breaking** change bumps the **MINOR** (`0.3.z` → `0.4.0`),
- an **additive** change or a **fix** bumps the **PATCH** (`0.3.1` → `0.3.2`).

A MINOR bump pre-1.0 means "read the CHANGELOG before upgrading." When the contract stabilizes we
cut **1.0.0** and switch to full SemVer guarantees (breaking → MAJOR only).

## Conventional Commits drive the bump

Commits (and, because we squash-merge, **pull-request titles** — see below) follow
[Conventional Commits](https://www.conventionalcommits.org):

| Type | Example | Bump |
| --- | --- | --- |
| `fix:` | `fix: reject an empty ENUM choices tuple` | PATCH |
| `feat:` | `feat: add a DATE field type` | MINOR |
| `feat!:` / `fix!:` / a `BREAKING CHANGE:` footer | `feat!: drop the deprecated Ctx.request escape hatch` | MAJOR (pre-1.0: MINOR) |
| `chore:` `docs:` `refactor:` `test:` `ci:` `style:` `build:` | `docs: clarify the Manifest.routes hook` | none |

> **Squash-merge caveat.** We merge PRs with **squash**, so the only commit that reaches `main` is
> the squash commit, whose message is the **PR title**. Therefore the **PR title** must be a valid
> Conventional Commit — it is what determines the version bump. A CI check enforces this (see
> `.github/workflows/pr-title.yml`). A PR that mixes an addition and a break takes the strongest
> type (`feat!:`).

## Releases

- The single source of version truth is `version` in `pyproject.toml`.
- A release is a **git tag `vX.Y.Z`** on `main`. The `[Unreleased]` section of
  [CHANGELOG.md](CHANGELOG.md) is renamed to that version + date at release time.
- Every PR that changes the public surface MUST add a `CHANGELOG.md` entry under `[Unreleased]`,
  classified Added / Changed / Removed / Fixed / **Deprecated**.
- (Planned) automated release via `release-please`, which reads the merged Conventional-Commit PR
  titles, computes the next version, updates the CHANGELOG, and opens a release PR. Deferred until
  the first tagged release — until then, versions are bumped by hand following the table above.

## Deprecation policy (Django-style)

We do not break silently. A public contract is removed only after a **deprecation window**:

1. **Deprecate** in a release: keep the old behavior working, mark it deprecated in the docstring
   and the CHANGELOG (`Deprecated`), and — where it is called at runtime — emit a
   `DeprecationWarning` naming the replacement and the removal version.
2. **Remove** no earlier than the **next MAJOR** (post-1.0) or the **next MINOR** (pre-1.0). Never
   in a PATCH.
3. Every deprecation names its **replacement** and its **planned removal version**, so an app
   author has a clear migration path and at least one release to take it.

## Core ↔ SDK compatibility (Terraform / OpenTelemetry-style)

The SDK and the core runtime version **independently** — the SDK is not lockstepped to core. Core
(and every app) declares the **range** of SDK versions it is compatible with:

- **Core** pins a compatible range in its dependencies, e.g. `moderatorim-sdk>=0.3,<0.4` (pre-1.0:
  pin to the current minor; post-1.0: `>=1.2,<2`).
- **An app** does the same: `moderatorim-sdk>=0.3,<0.4`.
- An SDK **MAJOR** bump (pre-1.0: **MINOR**) requires a **coordinated core release** that widens the
  pin in the same change set — core must never be published against an SDK range it has not been
  tested with.
- The compatibility expectation is documented here and in core's release notes; a future
  compatibility matrix (SDK version × core version) is added once there is more than one line to
  track.

## The mechanical guard

A test snapshots the exact set of `moderatorim.sdk.__all__` names (see the SDK's public-API test):
any add/remove trips it, forcing a conscious version + CHANGELOG decision before merge. Combined
with the PR-title Conventional-Commit lint, "you changed the contract" mechanically becomes "the
version and changelog reflect it."
