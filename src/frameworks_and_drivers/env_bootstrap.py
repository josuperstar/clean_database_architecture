from __future__ import annotations

from pathlib import Path


def load_application_dotenv() -> None:
    """Load ``.env`` from the repository root (first ancestor of this package that contains it)."""
    from dotenv import load_dotenv

    here = Path(__file__).resolve()
    for directory in here.parents:
        candidate = directory / ".env"
        if candidate.is_file():
            load_dotenv(candidate)
            return
    load_dotenv()