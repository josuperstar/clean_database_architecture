from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ListShotsRequestModel:
    project_id: str


@dataclass(frozen=True, slots=True)
class UpdateShotNameRequestModel:
    project_id: str
    shot_id: str
    new_name: str
    project_code: str = ""
