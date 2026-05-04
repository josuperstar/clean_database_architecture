from __future__ import annotations

import typer

from framework_and_drivers.cli.cli_shots_sink import CliShotsViewSink
from framework_and_drivers.composition.factory import (
    build_list_shots_controller_cli_capture,
    build_update_shot_name_controller,
)
from framework_and_drivers.tracking_presets import BACKEND_OPTIONS, FAKE_PROJECT_PRESETS
from interface_adapters.controllers.request_models import (
    ListShotsRequestModel,
    UpdateShotNameRequestModel,
)
from interface_adapters.view_models.list_shots_view_model import ShotRowViewModel


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


def _resolve_shot_row(
    rows: list[ShotRowViewModel], key: str
) -> tuple[ShotRowViewModel | None, str | None]:
    """Pick by 1-based index or exact current shot ``name`` (code)."""
    key = key.strip()
    if key.isdigit():
        n = int(key)
        if 1 <= n <= len(rows):
            return rows[n - 1], None
        return None, f"No shot #{n} (use 1–{len(rows)})."
    matches = [r for r in rows if r.name == key]
    if len(matches) == 1:
        return matches[0], None
    if not matches:
        return None, f"No shot named {key!r}; use a number from the list or the exact shot code."
    return None, f"Multiple shots named {key!r}; use a number (1–{len(rows)})."


def run_interactive_rename() -> None:
    """Prompt for source → project → shot, then new name and optional first-segment override."""
    typer.echo("\nSelect source (tracking backend):\n")
    for idx, (label, _t, _fv) in enumerate(BACKEND_OPTIONS, start=1):
        typer.echo(f"  {idx}) {label}")
    choice = _pick_int("Source number", 1, len(BACKEND_OPTIONS))
    _label, tracking, fake_vendor = BACKEND_OPTIONS[choice - 1]

    key = (tracking, fake_vendor or "")
    presets = FAKE_PROJECT_PRESETS.get(key, [])

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
    typer.echo(
        f"\nRename: shot number (1–{len(rows)}), or `<#> <new_name>`, "
        "or `<current_shot_code> <new_name>` (e.g. `3 SEQ02_99` or `SEQ02_30 SEQ02_99`)."
    )
    row: ShotRowViewModel | None = None
    new_name = ""
    while row is None or not new_name:
        raw = typer.prompt("Shot / new name", default="", show_default=False).strip()
        if not raw:
            typer.secho("Enter a value.", fg=typer.colors.RED, err=True)
            continue
        parts = raw.split(None, 1)
        if len(parts) == 2:
            key, new_name = parts[0], parts[1].strip()
            if not new_name:
                typer.secho("New name cannot be empty.", fg=typer.colors.RED, err=True)
                continue
            got, err = _resolve_shot_row(rows, key)
            if err:
                typer.secho(err, fg=typer.colors.RED, err=True)
                continue
            row = got
            assert row is not None
            break
        key = parts[0]
        got, err = _resolve_shot_row(rows, key)
        if err:
            typer.secho(err, fg=typer.colors.RED, err=True)
            continue
        row = got
        assert row is not None
        new_name = typer.prompt("New shot name (<sequence>_<digits>)").strip()
        if not new_name:
            typer.secho("New name is required.", fg=typer.colors.RED, err=True)
            row = None
            continue
        break

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
