from __future__ import annotations

from business_entities import (
    ProjectId,
    assert_shot_display_name_matches_nomenclature,
    infer_shot_name_first_token_from_shot,
)
from use_cases.ports.repositories import ShotRepository
from use_cases.ports.update_shot_name_output import UpdateShotNameOutputPort
from use_cases.update_shot_name.input import UpdateShotNameInput


class UpdateShotName:
    """Rename a shot after nomenclature and status business rules pass."""

    def __init__(self, shots: ShotRepository, output: UpdateShotNameOutputPort) -> None:
        self._shots = shots
        self._output = output

    def execute(self, data: UpdateShotNameInput) -> None:
        pid = data.project_id.strip()
        sid = data.shot_id.strip()
        new_name = data.new_name.strip()
        if not pid or not sid or not new_name:
            self._output.present_error("project_id, shot_id, and new_name are required.")
            return

        shot = self._shots.get_shot(ProjectId(pid), sid)
        if shot is None:
            self._output.present_error(f"No shot {sid!r} in project {pid!r}.")
            return
        if not shot.can_rename():
            self._output.present_error(
                "Cannot rename a shot while its status is in progress or done."
            )
            return

        explicit = data.project_code.strip()
        first_token = explicit if explicit else infer_shot_name_first_token_from_shot(shot)
        if not first_token:
            self._output.present_error(
                "Could not infer the first name segment from this shot (it needs a non-empty "
                "sequence). Pass --project-code / project_code to set the first token explicitly."
            )
            return

        try:
            assert_shot_display_name_matches_nomenclature(first_token, new_name)
        except ValueError as exc:
            self._output.present_error(str(exc))
            return

        try:
            self._shots.update_shot_name(ProjectId(pid), sid, new_name)
        except Exception as exc:  # noqa: BLE001 — boundary: surface as user-facing error
            self._output.present_error(str(exc))
            return

        self._output.present_renamed(pid, sid, new_name)
