from __future__ import annotations

from typing import Protocol


class UpdateShotNameOutputPort(Protocol):
    def present_renamed(self, project_id: str, shot_id: str, new_name: str) -> None: ...

    def present_error(self, message: str) -> None: ...
