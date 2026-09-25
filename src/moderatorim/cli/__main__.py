"""Enable ``python -m moderatorim`` (equivalent to the ``moderatorim`` console script)."""

from __future__ import annotations

from moderatorim.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
