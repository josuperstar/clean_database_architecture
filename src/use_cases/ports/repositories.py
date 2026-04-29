from typing import Protocol

from business_entities import ProjectId, Shot


class ShotRepository(Protocol):
    def list_shots(self, project_id: ProjectId) -> list[Shot]:
        """Return shots for the given project."""
        ...
