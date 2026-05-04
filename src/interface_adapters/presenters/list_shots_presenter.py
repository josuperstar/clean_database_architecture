from __future__ import annotations

from business_entities import Shot, ShotStatus
from interface_adapters.outward_interfaces.shots_view_sink import ShotsViewSink
from interface_adapters.view_models.list_shots_view_model import (
    ColorHint,
    FontEmphasis,
    ListShotsViewModel,
    ShotRowViewModel,
)
from use_cases.ports.list_shots_output import ListShotsOutputPort


def _status_label(status: ShotStatus) -> str:
    return {
        ShotStatus.IN_PROGRESS: "In progress",
        ShotStatus.READY_TO_START: "Ready to start",
        ShotStatus.DONE: "Done",
        ShotStatus.UNKNOWN: "Unknown",
    }[status]


def _color_for_status(status: ShotStatus) -> ColorHint:
    return {
        ShotStatus.IN_PROGRESS: ColorHint.BLUE,
        ShotStatus.READY_TO_START: ColorHint.GREEN,
        ShotStatus.DONE: ColorHint.GRAY,
        ShotStatus.UNKNOWN: ColorHint.AMBER,
    }[status]


class ListShotsPresenter(ListShotsOutputPort):
    """Builds a sorted `ListShotsViewModel` and pushes it through `ShotsViewSink` (no UI APIs)."""

    def __init__(self, sink: ShotsViewSink) -> None:
        self._sink = sink

    def present_shots(self, project_id: str, shots: list[Shot]) -> None:
        sorted_shots = sorted(shots, key=lambda s: s.name.casefold())
        rows: list[ShotRowViewModel] = []
        for shot in sorted_shots:
            rows.append(
                ShotRowViewModel(
                    shot_id=shot.id,
                    name=shot.name,
                    sequence=shot.sequence,
                    status_label=_status_label(shot.status),
                    color_hint=_color_for_status(shot.status),
                    font_emphasis=FontEmphasis.NORMAL,
                )
            )
        vm = ListShotsViewModel(project_id=project_id, rows=tuple(rows))
        self._sink.render(vm)

    def present_error(self, message: str) -> None:
        self._sink.render_error(message)
