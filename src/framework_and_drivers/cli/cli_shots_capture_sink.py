from __future__ import annotations

from dataclasses import dataclass

from interface_adapters.view_models.list_shots_view_model import ListShotsViewModel


@dataclass
class CliShotsCaptureSink:
    """Holds the last list result for interactive CLI (no terminal rendering)."""

    last_vm: ListShotsViewModel | None = None
    last_error: str | None = None

    def render(self, view_model: ListShotsViewModel) -> None:
        self.last_vm = view_model
        self.last_error = None

    def render_error(self, message: str) -> None:
        self.last_error = message
        self.last_vm = None
