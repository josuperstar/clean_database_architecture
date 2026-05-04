from __future__ import annotations

import typer

from framework_and_drivers.cli.interactive_rename import run_interactive_rename
from framework_and_drivers.composition.factory import (
    build_list_shots_controller,
    build_update_shot_name_controller,
)
from interface_adapters.controllers.request_models import (
    ListShotsRequestModel,
    UpdateShotNameRequestModel,
)

app = typer.Typer(
    help=(
        "List and rename shots (Clean Architecture demo). "
        "Run with no arguments for guided mode: pick source → project → see shots → rename "
        "(same as `shots-cli interactive`, aligned with Web/Qt)."
    ),
)


@app.callback(invoke_without_command=True)
def _main(ctx: typer.Context) -> None:
    """No subcommand: guided prompts; with `list` / `rename` / `interactive`, run that command."""
    if ctx.invoked_subcommand is None:
        run_interactive_rename()


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


@app.command("interactive")
def interactive() -> None:
    """Same as running `shots-cli` with no arguments: source → project → shots → rename."""
    run_interactive_rename()


@app.command("rename")
def rename_shot(
    project_id: str = typer.Argument(..., help="Project id (e.g. demo for fake ShotGrid)"),
    shot_id: str = typer.Argument(..., help="Shot id / external id in the tracker"),
    new_name: str = typer.Argument(..., help="New display name, must match <sequence>_<digits>"),
    project_code: str | None = typer.Option(
        None,
        "--project-code",
        "-c",
        help="Optional: override the first name segment (defaults to the shot's sequence; name must be <segment>_<digits>).",
    ),
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
    controller = build_update_shot_name_controller(
        tracking=tracking,
        fake_vendor=fake_vendor,
    )
    controller.handle(
        UpdateShotNameRequestModel(
            project_id=project_id,
            shot_id=shot_id,
            new_name=new_name,
            project_code=(project_code or "").strip(),
        )
    )


def run_cli() -> None:
    app()


if __name__ == "__main__":
    run_cli()
