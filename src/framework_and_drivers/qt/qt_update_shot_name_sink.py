from __future__ import annotations

from use_cases.ports.update_shot_name_output import UpdateShotNameOutputPort


class QtUpdateShotNameSink(UpdateShotNameOutputPort):
    """Shows rename success or errors on a ``QLabel`` (no stdout)."""

    def __init__(self, label: object) -> None:
        from PySide6.QtWidgets import QLabel  # noqa: PLC0415

        if not isinstance(label, QLabel):
            raise TypeError("label must be a PySide6.QtWidgets.QLabel")
        self._label = label

    def present_renamed(self, project_id: str, shot_id: str, new_name: str) -> None:
        self._label.setText(
            f"Renamed shot {shot_id} in project {project_id!r} to {new_name!r}."
        )
        self._label.setStyleSheet("color: #166534;")

    def present_error(self, message: str) -> None:
        self._label.setText(message)
        self._label.setStyleSheet("color: #b91c1c;")
