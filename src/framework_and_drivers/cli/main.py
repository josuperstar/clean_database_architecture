from __future__ import annotations

import typer

from framework_and_drivers.composition.factory import build_list_shots_controller
from interface_adapters.controllers.request_models import ListShotsRequestModel

app = typer.Typer(help="List shots for a project (Clean Architecture demo).")


@app.callback()
def _root() -> None:
    """Typer merges a lone @command into the root; this callback keeps `list` as a subcommand."""


@app.command("list")
def list_shots(
    project_id: str = typer.Argument(..., help="Project id or code"),
    tracking: str | None = typer.Option(
        None,
        "--tracking",
        "-t",
        help="Override TRACKING_BACKEND (fake|shotgun|ftrack|kitsu)",
    ),
    fake_vendor: str | None = typer.Option(
        None,
        "--fake-vendor",
        help="When tracking=fake: shotgun|ftrack|kitsu (or set FAKE_VENDOR)",
    ),
) -> None:
    controller = build_list_shots_controller(
        tracking=tracking,
        ui="cli",
        fake_vendor=fake_vendor,
    )
    controller.handle(ListShotsRequestModel(project_id=project_id))


def run_cli() -> None:
    app()


if __name__ == "__main__":
    run_cli()
