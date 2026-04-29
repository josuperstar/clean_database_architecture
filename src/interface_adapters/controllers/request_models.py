from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ListShotsRequestModel:
    project_id: str
