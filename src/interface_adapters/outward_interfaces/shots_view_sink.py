from typing import Protocol

from interface_adapters.view_models.list_shots_view_model import ListShotsViewModel


class ShotsViewSink(Protocol):
    def render(self, view_model: ListShotsViewModel) -> None: ...

    def render_error(self, message: str) -> None: ...
