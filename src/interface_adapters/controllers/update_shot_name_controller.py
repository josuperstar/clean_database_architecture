from __future__ import annotations

from interface_adapters.controllers.request_models import UpdateShotNameRequestModel
from use_cases.update_shot_name.input import UpdateShotNameInput
from use_cases.update_shot_name.update_shot_name import UpdateShotName


class UpdateShotNameController:
    def __init__(self, use_case: UpdateShotName) -> None:
        self._use_case = use_case

    def handle(self, request: UpdateShotNameRequestModel) -> None:
        data = UpdateShotNameInput(
            project_id=request.project_id,
            shot_id=request.shot_id,
            new_name=request.new_name,
            project_code=request.project_code,
        )
        self._use_case.execute(data)
