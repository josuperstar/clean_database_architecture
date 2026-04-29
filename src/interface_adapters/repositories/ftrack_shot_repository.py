from __future__ import annotations

from business_entities import ProjectId, Shot

from interface_adapters.outward_interfaces.ftrack_interface import FtrackDataPort
from interface_adapters.repositories._status_mapping import normalize_vendor_status


class FtrackBackedShotRepository:
    def __init__(self, ftrack: FtrackDataPort) -> None:
        self._ftrack = ftrack

    def list_shots(self, project_id: ProjectId) -> list[Shot]:
        rows = self._ftrack.find_shots_for_project(project_id)
        return [
            Shot(
                id=row.external_id,
                name=row.name,
                code=row.code,
                sequence=row.sequence,
                status=normalize_vendor_status(row.status_vendor, flavor="ftrack"),
            )
            for row in rows
        ]
