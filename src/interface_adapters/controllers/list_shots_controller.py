from __future__ import annotations

from interface_adapters.controllers.request_models import ListShotsRequestModel
from use_cases.list_shots.input import ListShotsInput
from use_cases.list_shots.list_shots_for_project import ListShotsForProject


class ListShotsController:
    def __init__(self, use_case: ListShotsForProject) -> None:
        self._use_case = use_case

    def handle(self, request: ListShotsRequestModel) -> None:
        data = ListShotsInput(project_id=request.project_id)
        self._use_case.execute(data)
