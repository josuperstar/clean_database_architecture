from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UpdateShotNameInput:
    """If empty, the first name segment defaults to the shot's ``sequence``; otherwise this overrides it (CLI/Web keep the name ``project_code`` for compatibility)."""

    project_id: str
    shot_id: str
    new_name: str
    project_code: str = ""
