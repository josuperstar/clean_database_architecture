from __future__ import annotations

from business_entities import ProjectId, Shot

from interface_adapters.outward_interfaces.kitsu_interface import KitsuDataPort
from interface_adapters.repositories._canonical_shot_label import canonical_shot_label
from interface_adapters.repositories.kitsu_shot_status import map_kitsu_shot_status


class KitsuBackedShotRepository:
    def __init__(self, kitsu: KitsuDataPort) -> None:
        self._kitsu = kitsu

    def list_shots(self, project_id: ProjectId) -> list[Shot]:
        rows = self._kitsu.find_shots_for_project(project_id)
        return [
            Shot(
                id=row.external_id,
                name=(label := canonical_shot_label(row)),
                code=label,
                sequence=row.sequence,
                status=map_kitsu_shot_status(row.status_vendor),
            )
            for row in rows
        ]

    def get_shot(self, project_id: ProjectId, shot_id: str) -> Shot | None:
        for shot in self.list_shots(project_id):
            if shot.id == shot_id:
                return shot
        return None

    def update_shot_name(self, project_id: ProjectId, shot_id: str, new_name: str) -> None:
        self._kitsu.update_shot_name(project_id, shot_id, new_name)
