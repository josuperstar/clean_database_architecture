from typing import Protocol

from business_entities import ProjectId, Shot


class ShotRepository(Protocol):
    def list_shots(self, project_id: ProjectId) -> list[Shot]:
        """Return shots for the given project."""
        ...

    def get_shot(self, project_id: ProjectId, shot_id: str) -> Shot | None:
        """Return a single shot by id, or ``None`` if it does not exist in the project."""
        ...

    def update_shot_name(self, project_id: ProjectId, shot_id: str, new_name: str) -> None:
        """Persist the shot display name (after business rules passed in the use case)."""
        ...
