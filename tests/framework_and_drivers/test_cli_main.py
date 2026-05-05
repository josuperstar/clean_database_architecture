from __future__ import annotations

from typer.testing import CliRunner

from framework_and_drivers.cli.main import app


def test_cli_list_subcommand_still_works() -> None:
    runner = CliRunner()
    r = runner.invoke(
        app,
        ["list", "demo", "--tracking", "fake", "--fake-vendor", "shotgun"],
    )
    assert r.exit_code == 0
    assert "Project: demo" in r.stdout
    assert "SEQ02_30" in r.stdout


def test_cli_no_args_runs_guided_flow() -> None:
    """Bare ``shots-cli`` invokes interactive rename (same as Web/Qt steps)."""
    runner = CliRunner()
    # 1) Fake ShotGrid, 2) project demo (first preset), 3) shot #3 + new name, 4) empty override
    user_input = "1\n1\n3 SEQ02_99\n\n"
    r = runner.invoke(app, [], input=user_input)
    assert r.exit_code == 0
    assert "SEQ02_99" in r.stdout or "Renamed" in r.stdout
