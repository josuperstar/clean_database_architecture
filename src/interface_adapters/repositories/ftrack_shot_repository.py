from __future__ import annotations

from business_entities import ProjectId, Shot

from interface_adapters.outward_interfaces.ftrack_interface import FtrackDataPort
from interface_adapters.repositories._canonical_shot_label import canonical_shot_label
from interface_adapters.repositories._status_mapping import normalize_vendor_status


class FtrackBackedShotRepository:
    def __init__(self, ftrack: FtrackDataPort) -> None:
        self._ftrack = ftrack

    def list_shots(self, project_id: ProjectId) -> list[Shot]:
        rows = self._ftrack.find_shots_for_project(project_id)
        return [
            Shot(
                id=row.external_id,
                name=(label := canonical_shot_label(row)),
                code=label,
                sequence=row.sequence,
                status=normalize_vendor_status(row.status_vendor, flavor="ftrack"),
            )
            for row in rows
        ]

    def get_shot(self, project_id: ProjectId, shot_id: str) -> Shot | None:
        for shot in self.list_shots(project_id):
            if shot.id == shot_id:
                return shot
        return None

    def update_shot_name(self, project_id: ProjectId, shot_id: str, new_name: str) -> None:
        self._ftrack.update_shot_name(project_id, shot_id, new_name)
