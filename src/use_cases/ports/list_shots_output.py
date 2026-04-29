from typing import Protocol

from business_entities import Shot


class ListShotsOutputPort(Protocol):
    def present_shots(self, project_id: str, shots: list[Shot]) -> None: ...

    def present_error(self, message: str) -> None: ...
