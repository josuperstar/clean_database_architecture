from __future__ import annotations

import os

from framework_and_drivers.composition import config_bootstrap
from interface_adapters.controllers.list_shots_controller import ListShotsController
from interface_adapters.controllers.update_shot_name_controller import UpdateShotNameController
from interface_adapters.presenters.list_shots_presenter import ListShotsPresenter
from interface_adapters.presenters.update_shot_name_presenter import (
    UpdateShotNamePresenter,
    WebRenamePresentationResult,
    WebUpdateShotNamePresenter,
)
from interface_adapters.repositories.ftrack_shot_repository import FtrackBackedShotRepository
from interface_adapters.repositories.kitsu_shot_repository import KitsuBackedShotRepository
from interface_adapters.repositories.shotgun_shot_repository import ShotgunBackedShotRepository
from use_cases.list_shots.list_shots_for_project import ListShotsForProject
from use_cases.ports.repositories import ShotRepository
from use_cases.update_shot_name.update_shot_name import UpdateShotName

from interface_adapters.outward_interfaces.raw_shot_row import RawShotRow

from framework_and_drivers.integrations.fake.fake_ftrack_client import FakeFtrackClient
from framework_and_drivers.integrations.fake.fake_kitsu_client import FakeKitsuClient
from framework_and_drivers.integrations.fake.fake_shotgun_client import FakeShotgunClient
from framework_and_drivers.integrations.ftrack.ftrack_client import FtrackClient
from framework_and_drivers.integrations.kitsu.kitsu_client import KitsuClient
from framework_and_drivers.integrations.shotgun.shotgun_client import ShotgunClient
from framework_and_drivers.cli.cli_shots_capture_sink import CliShotsCaptureSink
from framework_and_drivers.cli.cli_shots_sink import CliShotsViewSink
from framework_and_drivers.qt.qt_shots_sink import QtShotsViewSink
from framework_and_drivers.qt.qt_shots_table_sink import QtShotsTableSink
from framework_and_drivers.qt.qt_update_shot_name_sink import QtUpdateShotNameSink
from framework_and_drivers.web.web_shots_sink import WebPresentationResult, WebShotsViewSink

_CONFIG_BOOTSTRAP_DONE = False


def _ensure_config_bootstrapped() -> None:
    """Apply ``config.ini`` once (``setdefault``); existing env wins."""
    global _CONFIG_BOOTSTRAP_DONE
    if not _CONFIG_BOOTSTRAP_DONE:
        config_bootstrap.bootstrap_config_from_ini()
        _CONFIG_BOOTSTRAP_DONE = True


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
            RawShotRow("1", "SEQ01_10", "SEQ01_10", "SEQ01", "ip"),
            RawShotRow("2", "SEQ01_20", "SEQ01_20", "SEQ01", "fin"),
            RawShotRow("3", "SEQ02_30", "SEQ02_30", "SEQ02", "ready"),
        ],
    )
    return fake


def _fake_ftrack_with_demo_rows() -> FakeFtrackClient:
    """In-memory ftrack fake: project id `ftrack-demo`."""
    fake = FakeFtrackClient()
    fake.seed(
        "ftrack-demo",
        [
            RawShotRow("ft-1", "Edit_11", "Edit_11", "Edit", "wip"),
            RawShotRow("ft-2", "Anim_12", "Anim_12", "Anim", "ready"),
            RawShotRow("ft-3", "Delivery_13", "Delivery_13", "Delivery", "complete"),
        ],
    )
    return fake


def _fake_kitsu_with_demo_rows() -> FakeKitsuClient:
    """In-memory Kitsu fake: project id `kitsu-demo`."""
    fake = FakeKitsuClient()
    fake.seed(
        "kitsu-demo",
        [
            RawShotRow("kz-1", "Boards_21", "Boards_21", "Boards", "active"),
            RawShotRow("kz-2", "CG_22", "CG_22", "CG", "todo"),
            RawShotRow("kz-3", "Audio_23", "Audio_23", "Audio", "done"),
        ],
    )
    return fake


# One seeded fake client per vendor for the lifetime of the process. Qt (and the web app)
# build a new repository on each action; without sharing, rename would update store A while
# reload reads a fresh store B. Live trackers get a new HTTP client each time.
_PROCESS_FAKE_SHOTGUN: FakeShotgunClient | None = None
_PROCESS_FAKE_FTRACK: FakeFtrackClient | None = None
_PROCESS_FAKE_KITSU: FakeKitsuClient | None = None


def _shared_fake_shotgun() -> FakeShotgunClient:
    global _PROCESS_FAKE_SHOTGUN
    if _PROCESS_FAKE_SHOTGUN is None:
        _PROCESS_FAKE_SHOTGUN = _fake_shotgun_with_demo_rows()
    return _PROCESS_FAKE_SHOTGUN


def _shared_fake_ftrack() -> FakeFtrackClient:
    global _PROCESS_FAKE_FTRACK
    if _PROCESS_FAKE_FTRACK is None:
        _PROCESS_FAKE_FTRACK = _fake_ftrack_with_demo_rows()
    return _PROCESS_FAKE_FTRACK


def _shared_fake_kitsu() -> FakeKitsuClient:
    global _PROCESS_FAKE_KITSU
    if _PROCESS_FAKE_KITSU is None:
        _PROCESS_FAKE_KITSU = _fake_kitsu_with_demo_rows()
    return _PROCESS_FAKE_KITSU


def _build_shot_repository(
    *,
    tracking: str | None = None,
    fake_vendor: str | None = None,
) -> ShotRepository:
    _ensure_config_bootstrapped()
    t = (tracking or _tracking_from_env()).lower()
    fv = (fake_vendor or _fake_vendor_from_env()).lower()

    if t == "fake":
        if fv == "ftrack":
            return FtrackBackedShotRepository(_shared_fake_ftrack())
        if fv == "kitsu":
            return KitsuBackedShotRepository(_shared_fake_kitsu())
        return ShotgunBackedShotRepository(_shared_fake_shotgun())
    if t == "shotgun":
        return ShotgunBackedShotRepository(ShotgunClient())
    if t == "ftrack":
        return FtrackBackedShotRepository(FtrackClient())
    if t == "kitsu":
        return KitsuBackedShotRepository(KitsuClient())
    raise ValueError(f"Unknown TRACKING_BACKEND / tracking: {t!r}")


def build_list_shots_controller(
    *,
    tracking: str | None = None,
    ui: str,
    fake_vendor: str | None = None,
    web_result: WebPresentationResult | None = None,
) -> ListShotsController:
    """Wire repository (real or fake), presenter, use case, and controller for CLI or web."""
    repo = _build_shot_repository(tracking=tracking, fake_vendor=fake_vendor)

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


def build_list_shots_controller_cli_capture(
    *,
    tracking: str | None = None,
    fake_vendor: str | None = None,
) -> tuple[ListShotsController, CliShotsCaptureSink]:
    """List shots without printing; read ``sink.last_vm`` / ``sink.last_error`` after ``handle``."""
    repo = _build_shot_repository(tracking=tracking, fake_vendor=fake_vendor)
    sink = CliShotsCaptureSink()
    presenter = ListShotsPresenter(sink=sink)
    use_case = ListShotsForProject(repo, presenter)
    return ListShotsController(use_case), sink


def build_list_shots_controller_qt(
    *,
    shot_list_widget: object,
    tracking: str | None = None,
    fake_vendor: str | None = None,
) -> ListShotsController:
    """Pass a ``QTableWidget`` (selectable rows) or ``QTextEdit`` (HTML list)."""
    from PySide6.QtWidgets import QTableWidget, QTextEdit  # noqa: PLC0415

    repo = _build_shot_repository(tracking=tracking, fake_vendor=fake_vendor)

    if isinstance(shot_list_widget, QTextEdit):
        sink = QtShotsViewSink(shot_list_widget)
    elif isinstance(shot_list_widget, QTableWidget):
        sink = QtShotsTableSink(shot_list_widget)
    else:
        raise TypeError(
            "shot_list_widget must be PySide6 QTableWidget (recommended) or QTextEdit, "
            f"not {type(shot_list_widget).__name__}"
        )
    presenter = ListShotsPresenter(sink=sink)
    use_case = ListShotsForProject(repo, presenter)
    return ListShotsController(use_case)


def build_update_shot_name_controller(
    *,
    tracking: str | None = None,
    fake_vendor: str | None = None,
) -> UpdateShotNameController:
    repo = _build_shot_repository(tracking=tracking, fake_vendor=fake_vendor)
    presenter = UpdateShotNamePresenter()
    use_case = UpdateShotName(repo, presenter)
    return UpdateShotNameController(use_case)


def build_update_shot_name_controller_web(
    *,
    tracking: str | None = None,
    fake_vendor: str | None = None,
    web_result: WebRenamePresentationResult,
) -> UpdateShotNameController:
    repo = _build_shot_repository(tracking=tracking, fake_vendor=fake_vendor)
    presenter = WebUpdateShotNamePresenter(web_result)
    use_case = UpdateShotName(repo, presenter)
    return UpdateShotNameController(use_case)


def build_update_shot_name_controller_qt(
    *,
    status_label: object,
    tracking: str | None = None,
    fake_vendor: str | None = None,
) -> UpdateShotNameController:
    repo = _build_shot_repository(tracking=tracking, fake_vendor=fake_vendor)
    sink = QtUpdateShotNameSink(status_label)
    use_case = UpdateShotName(repo, sink)
    return UpdateShotNameController(use_case)


__all__ = [
    "build_list_shots_controller",
    "build_list_shots_controller_cli_capture",
    "build_list_shots_controller_qt",
    "build_update_shot_name_controller",
    "build_update_shot_name_controller_qt",
    "build_update_shot_name_controller_web",
]
