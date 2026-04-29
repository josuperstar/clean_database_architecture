from __future__ import annotations

from business_entities import ProjectId, Shot

from interface_adapters.outward_interfaces.kitsu_interface import KitsuDataPort
from interface_adapters.repositories._status_mapping import normalize_vendor_status


class KitsuBackedShotRepository:
    def __init__(self, kitsu: KitsuDataPort) -> None:
        self._kitsu = kitsu

    def list_shots(self, project_id: ProjectId) -> list[Shot]:
        rows = self._kitsu.find_shots_for_project(project_id)
        return [
            Shot(
                id=row.external_id,
                name=row.name,
                code=row.code,
                sequence=row.sequence,
                status=normalize_vendor_status(row.status_vendor, flavor="kitsu"),
            )
            for row in rows
        ]
