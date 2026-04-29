from __future__ import annotations

from business_entities import ProjectId
from use_cases.list_shots.input import ListShotsInput
from use_cases.ports.list_shots_output import ListShotsOutputPort
from use_cases.ports.repositories import ShotRepository


class ListShotsForProject:
    def __init__(self, shots: ShotRepository, output: ListShotsOutputPort) -> None:
        self._shots = shots
        self._output = output

    def execute(self, data: ListShotsInput) -> None:
        pid = data.project_id.strip()
        if not pid:
            self._output.present_error("project_id is required")
            return
        try:
            shots = self._shots.list_shots(ProjectId(pid))
        except Exception as exc:  # noqa: BLE001 — boundary: surface as user-facing error
            self._output.present_error(str(exc))
            return
        self._output.present_shots(pid, shots)
