"""Run: python -m framework_and_drivers.web (after install) or uvicorn framework_and_drivers.web.app:app."""

from __future__ import annotations

import uvicorn


def main() -> None:
    uvicorn.run("framework_and_drivers.web.app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
