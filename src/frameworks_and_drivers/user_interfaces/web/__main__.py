"""Run: python -m frameworks_and_drivers.user_interfaces.web (after install) or uvicorn with app path below."""

from __future__ import annotations

import uvicorn


def main() -> None:
    uvicorn.run(
        "frameworks_and_drivers.user_interfaces.web.app:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
