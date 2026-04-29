from __future__ import annotations

from business_entities import ProjectId, Shot

from interface_adapters.outward_interfaces.shotgun_interface import ShotgunDataPort
from interface_adapters.repositories._status_mapping import normalize_vendor_status


class ShotgunBackedShotRepository:
    def __init__(self, shotgun: ShotgunDataPort) -> None:
        self._shotgun = shotgun

    def list_shots(self, project_id: ProjectId) -> list[Shot]:
        rows = self._shotgun.find_shots_for_project(project_id)
        return [
            Shot(
                id=row.external_id,
                name=row.name,
                code=row.code,
                sequence=row.sequence,
                status=normalize_vendor_status(row.status_vendor, flavor="shotgun"),
            )
            for row in rows
        ]
