from __future__ import annotations

import typer

from framework_and_drivers.composition.factory import build_list_shots_controller
from framework_and_drivers.env_bootstrap import load_application_dotenv
from framework_and_drivers.tracking_sources import resolve_tracking_source
from interface_adapters.controllers.request_models import ListShotsRequestModel

app = typer.Typer(help="List shots for a project (Clean Architecture demo).")


@app.callback()
def _root() -> None:
    """Typer merges a lone @command into the root; this callback keeps `list` as a subcommand."""


@app.command("list")
def list_shots(
    project_id: str = typer.Argument(..., help="Project id or code"),
    source: str | None = typer.Option(
        None,
        "--source",
        "-s",
        help="Named backend (same ids as web ?source= and Qt). Overrides --tracking/--fake-vendor.",
    ),
    tracking: str | None = typer.Option(
        None,
        "--tracking",
        "-t",
        help="Override TRACKING_BACKEND (fake|shotgun|ftrack|kitsu); ignored if --source is set",
    ),
    fake_vendor: str | None = typer.Option(
        None,
        "--fake-vendor",
        help="When tracking=fake: shotgun|ftrack|kitsu; ignored if --source is set",
    ),
) -> None:
    try:
        eff_tracking, eff_fake = resolve_tracking_source(
            source=source, tracking=tracking, fake_vendor=fake_vendor
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    controller = build_list_shots_controller(
        tracking=eff_tracking,
        ui="cli",
        fake_vendor=eff_fake,
    )
    controller.handle(ListShotsRequestModel(project_id=project_id))


def run_cli() -> None:
    load_application_dotenv()
    app()


if __name__ == "__main__":
    run_cli()
