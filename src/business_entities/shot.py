from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ShotStatus(str, Enum):
    """Normalized lifecycle for presentation (colors) and parity across trackers."""

    IN_PROGRESS = "in_progress"
    READY_TO_START = "ready_to_start"
    DONE = "done"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Shot:
    """Tracking-agnostic shot; sort key for listing is `name` (alphabetical)."""

    id: str
    name: str
    code: str
    sequence: str | None
    status: ShotStatus
