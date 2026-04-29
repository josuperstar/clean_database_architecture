from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ListShotsInput:
    project_id: str
