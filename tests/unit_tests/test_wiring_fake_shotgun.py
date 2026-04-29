from __future__ import annotations

from frameworks_and_drivers.integrations.fake.fake_shotgun_client import FakeShotgunClient
from interface_adapters.controllers.list_shots_controller import ListShotsController
from interface_adapters.controllers.request_models import ListShotsRequestModel
from interface_adapters.outward_interfaces.raw_shot_row import RawShotRow
from interface_adapters.presenters.list_shots_presenter import ListShotsPresenter
from interface_adapters.repositories.shotgun_shot_repository import ShotgunBackedShotRepository
from interface_adapters.view_models.list_shots_view_model import ColorHint, ListShotsViewModel
from use_cases.list_shots.list_shots_for_project import ListShotsForProject


class RecordingSink:
    def __init__(self) -> None:
        self.vm: ListShotsViewModel | None = None
        self.error: str | None = None

    def render(self, view_model: ListShotsViewModel) -> None:
        self.vm = view_model

    def render_error(self, message: str) -> None:
        self.error = message


def test_fake_shotgun_through_repository_presenter_controller() -> None:
    fake = FakeShotgunClient()
    fake.seed(
        "42",
        [
            RawShotRow("1", "Zed", "Z", "SQ", "ip"),
            RawShotRow("2", "Amy", "A", None, "ready"),
        ],
    )
    repo = ShotgunBackedShotRepository(fake)
    sink = RecordingSink()
    presenter = ListShotsPresenter(sink=sink)
    uc = ListShotsForProject(repo, presenter)
    controller = ListShotsController(uc)
    controller.handle(ListShotsRequestModel(project_id="42"))

    assert sink.error is None
    assert sink.vm is not None
    names = [r.name for r in sink.vm.rows]
    assert names == ["Amy", "Zed"]
    assert sink.vm.rows[0].color_hint == ColorHint.GREEN
    assert sink.vm.rows[1].color_hint == ColorHint.BLUE
    assert sink.vm.rows[0].status_label == "Ready to start"
    assert sink.vm.rows[1].status_label == "In progress"


def test_status_unknown_maps_to_amber() -> None:
    fake = FakeShotgunClient()
    fake.seed("1", [RawShotRow("9", "Only", "O", None, "weird_vendor_status")])
    repo = ShotgunBackedShotRepository(fake)
    sink = RecordingSink()
    uc = ListShotsForProject(repo, ListShotsPresenter(sink=sink))
    ListShotsController(uc).handle(ListShotsRequestModel(project_id="1"))
    assert sink.vm is not None
    assert sink.vm.rows[0].color_hint == ColorHint.AMBER
