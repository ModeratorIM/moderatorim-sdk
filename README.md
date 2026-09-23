# moderatorim-sdk

The **ModeratorIM app SDK** — the contract kernel you build ModeratorIM apps against.

An app depends on this package alone. It gives you the types you author with:

```python
from moderatorim.sdk import Manifest, UnitType, NavEntry, App, Ctx, Page, redirect, Model, Field
```

You never import the ModeratorIM core runtime. Core implements these contracts and, at runtime,
hands your handlers a live `Ctx` (the data store, the current user, the permission check) — so your
app reaches core's behavior without depending on it.

`moderatorim` is a shared namespace: this package provides `moderatorim.sdk`; the core runtime
provides `moderatorim.core`. Installing this SDK does **not** install the core runtime.

## Install

```
pip install moderatorim-sdk
```

## License

AGPL-3.0-or-later.
