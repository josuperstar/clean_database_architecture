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
    """
    Tracking-agnostic shot; sort key for listing is `name` (alphabetical).

    ``name`` and ``code`` are the same studio-facing label (interface adapters map
    tracker name/code into both fields identically). Rename nomenclature is
    ``<sequence>_<digits>`` using ``sequence`` as the first segment unless overridden.
    """

    id: str
    name: str
    code: str
    sequence: str | None
    status: ShotStatus

    def can_rename(self) -> bool:
        """Domain rule: renaming is blocked for in-progress and done shots."""
        return self.status not in (ShotStatus.IN_PROGRESS, ShotStatus.DONE)
