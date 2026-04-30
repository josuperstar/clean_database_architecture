from __future__ import annotations

import typer

from framework_and_drivers.cli.cli_shots_sink import CliShotsViewSink
from framework_and_drivers.composition.factory import (
    build_list_shots_controller_cli_capture,
    build_update_shot_name_controller,
)
from interface_adapters.controllers.request_models import (
    ListShotsRequestModel,
    UpdateShotNameRequestModel,
)

# (label, tracking, fake_vendor when tracking is fake; else None) — same order as Qt demo.
_BACKEND_OPTIONS: list[tuple[str, str, str | None]] = [
    ("Fake ShotGrid (in-memory)", "fake", "shotgun"),
    ("Fake ftrack (in-memory)", "fake", "ftrack"),
    ("Fake Kitsu (in-memory)", "fake", "kitsu"),
    ("ShotGrid / Shotgun (live API)", "shotgun", None),
    ("ftrack (live API)", "ftrack", None),
    ("Kitsu (live API)", "kitsu", None),
]

_FAKE_PROJECT_PRESETS: dict[tuple[str, str], list[str]] = {
    ("fake", "shotgun"): ["demo"],
    ("fake", "ftrack"): ["ftrack-demo"],
    ("fake", "kitsu"): ["kitsu-demo"],
}


def _pick_int(prompt: str, lo: int, hi: int) -> int:
    while True:
        raw = typer.prompt(prompt).strip()
        try:
            n = int(raw)
            if lo <= n <= hi:
                return n
        except ValueError:
            pass
        typer.secho(f"Enter an integer from {lo} to {hi}.", fg=typer.colors.RED, err=True)


def run_interactive_rename() -> None:
    """Prompt for source → project → shot, then new name and optional first-segment override."""
    typer.echo("\nSelect source (tracking backend):\n")
    for idx, (label, _t, _fv) in enumerate(_BACKEND_OPTIONS, start=1):
        typer.echo(f"  {idx}) {label}")
    choice = _pick_int("Source number", 1, len(_BACKEND_OPTIONS))
    _label, tracking, fake_vendor = _BACKEND_OPTIONS[choice - 1]

    key = (tracking, fake_vendor or "")
    presets = _FAKE_PROJECT_PRESETS.get(key, [])

    typer.echo(f"\nSelected: {_label}\n")
    project_id = ""
    if presets:
        typer.echo("Select project:\n")
        for i, pid in enumerate(presets, start=1):
            typer.echo(f"  {i}) {pid}")
        other = len(presets) + 1
        typer.echo(f"  {other}) Other (type project id)")
        pchoice = _pick_int("Project number", 1, other)
        if pchoice <= len(presets):
            project_id = presets[pchoice - 1]
        else:
            project_id = typer.prompt("Project id").strip()
    else:
        project_id = typer.prompt("Project id").strip()

    if not project_id:
        typer.secho("Project id is required.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    list_ctrl, cap = build_list_shots_controller_cli_capture(
        tracking=tracking,
        fake_vendor=fake_vendor,
    )
    list_ctrl.handle(ListShotsRequestModel(project_id=project_id))
    if cap.last_error:
        typer.secho(cap.last_error, fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    if cap.last_vm is None:
        typer.secho("No list result.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    rows = list(cap.last_vm.rows)
    if not rows:
        typer.secho("No shots in that project.", fg=typer.colors.YELLOW, err=True)
        raise typer.Exit(code=1)

    typer.echo("\nShots (same colors as `shots-cli list`):\n")
    CliShotsViewSink().render_shot_picker(cap.last_vm)
    typer.echo("\nSelect shot to rename.")
    schoice = _pick_int("Shot number", 1, len(rows))
    row = rows[schoice - 1]

    new_name = typer.prompt("New shot name (<sequence>_<digits>)").strip()
    if not new_name:
        typer.secho("New name is required.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    override = typer.prompt(
        "First name segment override (Enter for shot sequence)",
        default="",
        show_default=False,
    ).strip()

    rename_ctrl = build_update_shot_name_controller(
        tracking=tracking,
        fake_vendor=fake_vendor,
    )
    rename_ctrl.handle(
        UpdateShotNameRequestModel(
            project_id=project_id,
            shot_id=row.shot_id,
            new_name=new_name,
            project_code=override,
        )
    )
