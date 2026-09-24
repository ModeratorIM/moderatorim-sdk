# Changelog

All notable changes to `moderatorim-sdk` are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) from `1.0.0` onward.

> **Pre-1.0:** the contract surface is unstable. Breaking changes may land in any `0.0.x` release
> and are noted here.

## [Unreleased]

## [0.1.0] — 2026-09-24

### Added
- Initial contract kernel, extracted from the ModeratorIM core:
  - `models` — `Model`, `Field`/`FieldType` (+ `ref`/`enum`/`list_of`), `Extends`,
    `ResolvedSchema`/`ResolvedColumn`.
  - `datastore` — the `DataStore` port + `Filter`/`FilterOp`.
  - `bus` — `Event`/`EventKind`, `Action`/`ActionKind`, `EventBus`.
  - `registry` — `Manifest` (with the `routes` hook), `UnitType`, `NavEntry`.
  - `web` — the `App` routing facade + `Ctx`/`Page`/`Fragment`/`Rendered`/`redirect`.
- Domain-driven folder layout mirroring core; flat public API via `from moderatorim.sdk import ...`.
