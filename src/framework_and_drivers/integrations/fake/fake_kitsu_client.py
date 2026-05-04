from __future__ import annotations

from business_entities import ProjectId

from framework_and_drivers.integrations.fake._memory_store import InMemoryShotStore
from interface_adapters.outward_interfaces.kitsu_interface import KitsuDataPort
from interface_adapters.outward_interfaces.raw_shot_row import RawShotRow


class FakeKitsuClient(KitsuDataPort):
    def __init__(
        self,
        store: InMemoryShotStore | None = None,
        *,
        initial: dict[str, list[RawShotRow]] | None = None,
    ) -> None:
        self._store = store or InMemoryShotStore(initial)

    def seed(self, project_id: str, rows: list[RawShotRow]) -> None:
        self._store.seed(project_id, rows)

    def find_shots_for_project(self, project_id: ProjectId) -> list[RawShotRow]:
        return self._store.find(project_id)

    def update_shot_name(self, project_id: ProjectId, shot_external_id: str, new_name: str) -> None:
        self._store.update_shot_name(project_id, shot_external_id, new_name)
