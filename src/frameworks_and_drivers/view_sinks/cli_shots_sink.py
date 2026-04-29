from __future__ import annotations

import sys

from interface_adapters.view_models.list_shots_view_model import ColorHint, ListShotsViewModel


class CliShotsViewSink:
    """Maps `ColorHint` to ANSI sequences for capable terminals."""

    _ANSI = {
        ColorHint.BLUE: "\033[34m",
        ColorHint.GREEN: "\033[32m",
        ColorHint.GRAY: "\033[90m",
        ColorHint.AMBER: "\033[33m",
        ColorHint.NEUTRAL: "\033[0m",
    }
    _RESET = "\033[0m"

    def render(self, view_model: ListShotsViewModel) -> None:
        out = sys.stdout
        print(f"Project: {view_model.project_id}", file=out)
        for row in view_model.rows:
            color = self._ANSI.get(row.color_hint, self._RESET)
            line = f"{color}{row.name} ({row.code}) — {row.status_label}{self._RESET}"
            print(line, file=out)

    def render_error(self, message: str) -> None:
        print(message, file=sys.stderr)
