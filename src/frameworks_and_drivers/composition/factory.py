from __future__ import annotations

import os
from interface_adapters.controllers.list_shots_controller import ListShotsController
from interface_adapters.presenters.list_shots_presenter import ListShotsPresenter
from interface_adapters.repositories.ftrack_shot_repository import FtrackBackedShotRepository
from interface_adapters.repositories.kitsu_shot_repository import KitsuBackedShotRepository
from interface_adapters.repositories.shotgun_shot_repository import ShotgunBackedShotRepository
from use_cases.list_shots.list_shots_for_project import ListShotsForProject

from interface_adapters.outward_interfaces.raw_shot_row import RawShotRow

from frameworks_and_drivers.integrations.fake.fake_ftrack_client import FakeFtrackClient
from frameworks_and_drivers.integrations.fake.fake_kitsu_client import FakeKitsuClient
from frameworks_and_drivers.integrations.fake.fake_shotgun_client import FakeShotgunClient
from frameworks_and_drivers.integrations.ftrack.ftrack_client import FtrackClient
from frameworks_and_drivers.integrations.kitsu.kitsu_client import KitsuClient
from frameworks_and_drivers.integrations.shotgun.shotgun_client import ShotgunClient
from frameworks_and_drivers.view_sinks.cli_shots_sink import CliShotsViewSink
from frameworks_and_drivers.view_sinks.qt_shots_sink import QtShotsViewSink
from frameworks_and_drivers.view_sinks.web_shots_sink import WebPresentationResult, WebShotsViewSink


def _tracking_from_env() -> str:
    return os.environ.get("TRACKING_BACKEND", "fake").strip().lower()


def _fake_vendor_from_env() -> str:
    return os.environ.get("FAKE_VENDOR", "shotgun").strip().lower()


def _fake_shotgun_with_demo_rows() -> FakeShotgunClient:
    """In-memory ShotGrid fake: project id `demo`."""
    fake = FakeShotgunClient()
    fake.seed(
        "demo",
        [
            RawShotRow("1", "Opening", "OPN", "SEQ01", "ip"),
            RawShotRow("2", "Hero beat", "HRB", "SEQ01", "fin"),
            RawShotRow("3", "Pickup wide", "PUW", "SEQ02", "ready"),
        ],
    )
    return fake


def _fake_ftrack_with_demo_rows() -> FakeFtrackClient:
    """In-memory ftrack fake: project id `ftrack-demo`."""
    fake = FakeFtrackClient()
    fake.seed(
        "ftrack-demo",
        [
            RawShotRow("ft-1", "Build review", "BRV", "Edit", "wip"),
            RawShotRow("ft-2", "Anim blocking", "ABK", "Anim", "ready"),
            RawShotRow("ft-3", "Client delivery", "CLD", "Delivery", "complete"),
        ],
    )
    return fake


def _fake_kitsu_with_demo_rows() -> FakeKitsuClient:
    """In-memory Kitsu fake: project id `kitsu-demo`."""
    fake = FakeKitsuClient()
    fake.seed(
        "kitsu-demo",
        [
            RawShotRow("kz-1", "Story reel", "SRL", "Boards", "active"),
            RawShotRow("kz-2", "Lighting pass", "LGT", "CG", "todo"),
            RawShotRow("kz-3", "Final mix", "MIX", "Audio", "done"),
        ],
    )
    return fake


def build_list_shots_controller(
    *,
    tracking: str | None = None,
    ui: str,
    fake_vendor: str | None = None,
    web_result: WebPresentationResult | None = None,
) -> ListShotsController:
    """Wire repository (real or fake), presenter, use case, and controller for CLI or web."""
    t = (tracking or _tracking_from_env()).lower()
    fv = (fake_vendor or _fake_vendor_from_env()).lower()

    if t == "fake":
        if fv == "ftrack":
            repo = FtrackBackedShotRepository(_fake_ftrack_with_demo_rows())
        elif fv == "kitsu":
            repo = KitsuBackedShotRepository(_fake_kitsu_with_demo_rows())
        else:
            repo = ShotgunBackedShotRepository(_fake_shotgun_with_demo_rows())
    elif t == "shotgun":
        repo = ShotgunBackedShotRepository(ShotgunClient())
    elif t == "ftrack":
        repo = FtrackBackedShotRepository(FtrackClient())
    elif t == "kitsu":
        repo = KitsuBackedShotRepository(KitsuClient())
    else:
        raise ValueError(f"Unknown TRACKING_BACKEND / tracking: {t!r}")

    if ui == "cli":
        sink = CliShotsViewSink()
    elif ui == "web":
        if web_result is None:
            raise ValueError("web_result is required when ui='web'")
        sink = WebShotsViewSink(web_result)
    else:
        raise ValueError(f"Unknown ui: {ui!r} (use build_list_shots_controller_qt for Qt)")

    presenter = ListShotsPresenter(sink=sink)
    use_case = ListShotsForProject(repo, presenter)
    return ListShotsController(use_case)


def build_list_shots_controller_qt(
    *,
    text_edit: object,
    tracking: str | None = None,
    fake_vendor: str | None = None,
) -> ListShotsController:
    t = (tracking or _tracking_from_env()).lower()
    fv = (fake_vendor or _fake_vendor_from_env()).lower()

    if t == "fake":
        if fv == "ftrack":
            repo = FtrackBackedShotRepository(_fake_ftrack_with_demo_rows())
        elif fv == "kitsu":
            repo = KitsuBackedShotRepository(_fake_kitsu_with_demo_rows())
        else:
            repo = ShotgunBackedShotRepository(_fake_shotgun_with_demo_rows())
    elif t == "shotgun":
        repo = ShotgunBackedShotRepository(ShotgunClient())
    elif t == "ftrack":
        repo = FtrackBackedShotRepository(FtrackClient())
    elif t == "kitsu":
        repo = KitsuBackedShotRepository(KitsuClient())
    else:
        raise ValueError(f"Unknown tracking backend: {t!r}")

    sink = QtShotsViewSink(text_edit)
    presenter = ListShotsPresenter(sink=sink)
    use_case = ListShotsForProject(repo, presenter)
    return ListShotsController(use_case)


__all__ = ["build_list_shots_controller", "build_list_shots_controller_qt"]
