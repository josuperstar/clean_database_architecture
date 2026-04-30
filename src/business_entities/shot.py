from __future__ import annotations

import re
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
    tracker name/code into both fields identically).

    **Rename nomenclature:** a new display name must be ``<first_token>_<digits>``.
    ``first_token`` defaults to the trimmed ``sequence``; callers may pass an override
    (CLI ``--project-code`` / Web ``project_code``). See ``resolve_rename_first_token`` and
    ``assert_display_name_matches_nomenclature``.
    """

    id: str
    name: str
    code: str
    sequence: str | None
    status: ShotStatus

    def can_rename(self) -> bool:
        """Domain rule: renaming is blocked for in-progress and done shots."""
        return self.status not in (ShotStatus.IN_PROGRESS, ShotStatus.DONE)

    def infer_rename_first_token(self) -> str | None:
        """First segment of a valid new name: trimmed ``sequence``, or ``None`` if absent."""
        seq = (self.sequence or "").strip()
        return seq or None

    def resolve_rename_first_token(self, override: str = "") -> str | None:
        """Non-empty ``override`` wins; otherwise same as ``infer_rename_first_token``."""
        o = override.strip()
        if o:
            return o
        return self.infer_rename_first_token()

    @staticmethod
    def assert_display_name_matches_nomenclature(first_token: str, new_name: str) -> None:
        """
        ``new_name`` must be exactly ``<first_token>_<digits>`` (regex-safe literal match on
        ``first_token``).
        """
        token = first_token.strip()
        name = new_name.strip()
        if not token:
            raise ValueError("First name segment (sequence) is required for nomenclature validation.")
        pattern = re.compile(rf"^{re.escape(token)}_\d+$")
        if not pattern.fullmatch(name):
            raise ValueError(
                f"Shot name must match {token!r}_<digits> (e.g. {token}_01). Got {name!r}."
            )
