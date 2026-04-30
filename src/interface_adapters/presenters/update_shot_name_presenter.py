from __future__ import annotations

import sys
from dataclasses import dataclass

from use_cases.ports.update_shot_name_output import UpdateShotNameOutputPort


class UpdateShotNamePresenter(UpdateShotNameOutputPort):
    """CLI-oriented presenter: messages to stdout / stderr."""

    def present_renamed(self, project_id: str, shot_id: str, new_name: str) -> None:
        print(
            f"Renamed shot {shot_id} in project {project_id!r} to {new_name!r}.",
            file=sys.stdout,
        )

    def present_error(self, message: str) -> None:
        print(message, file=sys.stderr)


@dataclass
class WebRenamePresentationResult:
    """Mutable holder FastAPI reads after ``controller.handle(...)`` for rename."""

    message: str | None = None
    error: str | None = None


class WebUpdateShotNamePresenter(UpdateShotNameOutputPort):
    """Fills ``WebRenamePresentationResult`` for JSON responses (no stdout)."""

    def __init__(self, result: WebRenamePresentationResult) -> None:
        self._result = result

    def present_renamed(self, project_id: str, shot_id: str, new_name: str) -> None:
        self._result.error = None
        self._result.message = (
            f"Renamed shot {shot_id} in project {project_id!r} to {new_name!r}."
        )

    def present_error(self, message: str) -> None:
        self._result.error = message
        self._result.message = None
