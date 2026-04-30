from typing import Protocol

from business_entities import ProjectId

from interface_adapters.outward_interfaces.raw_shot_row import RawShotRow


class FtrackDataPort(Protocol):
    def find_shots_for_project(self, project_id: ProjectId) -> list[RawShotRow]:
        ...

    def update_shot_name(self, project_id: ProjectId, shot_external_id: str, new_name: str) -> None:
        ...
