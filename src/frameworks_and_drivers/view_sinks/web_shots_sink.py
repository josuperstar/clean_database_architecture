from __future__ import annotations

from dataclasses import dataclass

from interface_adapters.view_models.list_shots_view_model import ListShotsViewModel


@dataclass
class WebPresentationResult:
    """Mutable holder FastAPI reads after `controller.handle(...)`."""

    view_model: ListShotsViewModel | None = None
    error: str | None = None


class WebShotsViewSink:
    def __init__(self, result: WebPresentationResult) -> None:
        self._result = result

    def render(self, view_model: ListShotsViewModel) -> None:
        self._result.view_model = view_model
        self._result.error = None

    def render_error(self, message: str) -> None:
        self._result.error = message
        self._result.view_model = None
