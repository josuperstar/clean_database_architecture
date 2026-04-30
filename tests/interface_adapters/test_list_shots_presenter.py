from __future__ import annotations

from business_entities import Shot, ShotStatus
from interface_adapters.presenters.list_shots_presenter import ListShotsPresenter
from interface_adapters.view_models.list_shots_view_model import ColorHint, ListShotsViewModel


class RecordingSink:
    def __init__(self) -> None:
        self.vm: ListShotsViewModel | None = None
        self.error: str | None = None

    def render(self, view_model: ListShotsViewModel) -> None:
        self.vm = view_model

    def render_error(self, message: str) -> None:
        self.error = message


def test_presenter_sorts_alphabetically_and_maps_colors() -> None:
    sink = RecordingSink()
    presenter = ListShotsPresenter(sink=sink)
    shots = [
        Shot(id="2", name="Bravo", code="Bravo", sequence="SQ01", status=ShotStatus.IN_PROGRESS),
        Shot(id="1", name="Alpha", code="Alpha", sequence=None, status=ShotStatus.READY_TO_START),
        Shot(id="3", name="Charlie", code="Charlie", sequence=None, status=ShotStatus.DONE),
    ]
    presenter.present_shots("proj-x", shots)
    assert sink.vm is not None
    assert sink.vm.project_id == "proj-x"
    names = [r.name for r in sink.vm.rows]
    assert names == ["Alpha", "Bravo", "Charlie"]
    assert sink.vm.rows[0].color_hint == ColorHint.GREEN
    assert sink.vm.rows[1].color_hint == ColorHint.BLUE
    assert sink.vm.rows[2].color_hint == ColorHint.GRAY


def test_present_error() -> None:
    sink = RecordingSink()
    presenter = ListShotsPresenter(sink=sink)
    presenter.present_error("oops")
    assert sink.error == "oops"
