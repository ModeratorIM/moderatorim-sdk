"""ModeratorIM app SDK — the contract kernel external apps build against.

An app imports ONLY from this package (``from moderatorim.sdk import Manifest, App, Ctx, Page,
Model, ...``); it never imports ``moderatorim.core``. Core implements these contracts and injects
live handles (the ``Ctx``) at runtime, so an app reaches core's behavior without depending on it.

``moderatorim`` is a PEP 420 namespace shared with ``moderatorim-core`` — this package owns only
``moderatorim.sdk``. The curated public surface is populated as the contract modules are moved in
(SDK tasks P1–P2).
"""

__all__: list[str] = []
