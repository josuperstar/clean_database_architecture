from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RawShotRow:
    """Neutral row from a tracking integration before mapping to `Shot`."""

    external_id: str
    name: str
    code: str
    sequence: str | None
    status_vendor: str
