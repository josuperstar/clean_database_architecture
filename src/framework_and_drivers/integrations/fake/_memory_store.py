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

    def update_shot_name(self, project_id: ProjectId, shot_id: str, new_name: str) -> None:
        pid = str(project_id)
        rows = self._by_project.get(pid)
        if rows is None:
            raise LookupError(pid)
        for i, row in enumerate(rows):
            if row.external_id == shot_id:
                rows[i] = RawShotRow(
                    row.external_id,
                    new_name,
                    new_name,
                    row.sequence,
                    row.status_vendor,
                )
                return
        raise LookupError(shot_id)
