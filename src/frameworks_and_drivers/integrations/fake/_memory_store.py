from __future__ import annotations

from business_entities import ProjectId

from interface_adapters.outward_interfaces.raw_shot_row import RawShotRow


class InMemoryShotStore:
    """Shared in-memory backing for Fake* clients."""

    def __init__(self, initial: dict[str, list[RawShotRow]] | None = None) -> None:
        self._by_project: dict[str, list[RawShotRow]] = {
            k: list(v) for k, v in (initial or {}).items()
        }

    def seed(self, project_id: str, rows: list[RawShotRow]) -> None:
        self._by_project[project_id] = list(rows)

    def find(self, project_id: ProjectId) -> list[RawShotRow]:
        return list(self._by_project.get(str(project_id), []))
