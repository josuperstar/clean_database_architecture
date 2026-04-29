from typing import Protocol

from business_entities import ProjectId

from interface_adapters.outward_interfaces.raw_shot_row import RawShotRow


class KitsuDataPort(Protocol):
    def find_shots_for_project(self, project_id: ProjectId) -> list[RawShotRow]:
        ...
