# Versioning

This page tells you, as a **ModeratorIM app developer**, what `moderatorim-sdk`'s version numbers
promise and how to depend on the SDK safely. (Maintainer release process lives in
[RELEASING.md](RELEASING.md).)

`moderatorim-sdk` is the contract your app builds against — the version number is a compatibility
promise, so you can reason about upgrades from the number alone.

## What the numbers mean (SemVer)

Versions are [SemVer 2.0](https://semver.org): **`MAJOR.MINOR.PATCH`**. For this package the
"public API" is everything you import from `moderatorim.sdk` (the names in its `__all__`) and the
shape of each — a dataclass's fields, the `DataStore` method signatures, an enum's members,
`Ctx`'s attributes, and the validation rules your declarations must satisfy.

| If the version goes… | It means | What you should do |
| --- | --- | --- |
| **PATCH** (`0.3.1` → `0.3.2`) | A fix or internal change. Nothing in the API you use changed. | Upgrade freely. |
| **MINOR** (`0.3.2` → `0.4.0` pre-1.0; `1.3` → `1.4` after) | New things were **added**; existing things still work. | Upgrade freely — nothing you use breaks. Read the CHANGELOG to see what's new. |
| **MAJOR** (`1.x` → `2.0`) | A **breaking** change — something was removed, renamed, or its shape changed. | Read the CHANGELOG's `Removed`/`Changed` + the migration notes before upgrading. |

### We are pre-1.0 — read this

While the version is `0.y.z`, **the contract is not yet stable**. To keep the signal useful during
this phase we bump deliberately: a **breaking** change bumps the **MINOR** (`0.3.z` → `0.4.0`), and
additions or fixes bump the **PATCH**. So **treat a MINOR bump pre-1.0 as "there may be a breaking
change — read the CHANGELOG before upgrading."** Once the API stabilizes we cut **1.0.0** and switch
to the full guarantees above (breaking changes only ever in a MAJOR).

## Pinning the SDK in your app

Depend on a **compatible range**, not an exact version or an open range — pin to the minor while
pre-1.0, and to the major once the SDK reaches 1.0:

```toml
# your app's pyproject.toml — pre-1.0 (pin to the current minor):
dependencies = ["moderatorim-sdk>=0.4,<0.5"]

# once the SDK is 1.0+ (pin to the major):
# dependencies = ["moderatorim-sdk>=1.2,<2"]
```

This lets you take PATCH and (pre-1.0: not MINOR) updates automatically while never being surprised
by a breaking one. The ModeratorIM **core** you run your app on pins the SDK the same way, so match
your app's range to the SDK version your target core supports (core's release notes state it).

## When something is going away (deprecation policy)

We don't break you silently. Before any public thing is removed, it goes through a **deprecation
window** (Django-style):

1. It is first **marked deprecated** in a release — it keeps working, the CHANGELOG lists it under
   `Deprecated`, its docstring says so, and (where it runs) it emits a `DeprecationWarning` that
   **names the replacement and the version it will be removed in**.
2. It is **removed no earlier than the next MAJOR** (pre-1.0: the next MINOR) — never in a PATCH.

So you always get at least one release with a warning + a named migration path before anything you
depend on disappears. **Run your tests with deprecation warnings visible** (`pytest -W error::DeprecationWarning`
during development) to catch these early.

## Staying informed

- **[CHANGELOG.md](CHANGELOG.md)** — every release's Added / Changed / Removed / Deprecated / Fixed.
- **Releases** — each version is a git tag `vX.Y.Z`; watch the repo's Releases for notes.
- Pre-1.0, skim the CHANGELOG on **every** upgrade; post-1.0, you only need to on a MAJOR.
