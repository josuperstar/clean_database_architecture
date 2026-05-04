from __future__ import annotations

from business_entities import ProjectId, Shot, ShotStatus
from use_cases.list_shots.input import ListShotsInput
from use_cases.list_shots.list_shots_for_project import ListShotsForProject


class FakeShotRepository:
    def __init__(self, shots: list[Shot]) -> None:
        self._shots = shots
        self.calls: list[str] = []

    def list_shots(self, project_id: ProjectId) -> list[Shot]:
        self.calls.append(str(project_id))
        return list(self._shots)

    def get_shot(self, project_id: ProjectId, shot_id: str) -> Shot | None:
        return next((s for s in self._shots if s.id == shot_id), None)

    def update_shot_name(self, project_id: ProjectId, shot_id: str, new_name: str) -> None:
        pass


class SpyOutput:
    def __init__(self) -> None:
        self.shots_calls: list[tuple[str, list[Shot]]] = []
        self.errors: list[str] = []

    def present_shots(self, project_id: str, shots: list[Shot]) -> None:
        self.shots_calls.append((project_id, list(shots)))

    def present_error(self, message: str) -> None:
        self.errors.append(message)


def test_execute_lists_shots() -> None:
    shots = [
        Shot(id="1", name="Zebra", code="Zebra", sequence=None, status=ShotStatus.DONE),
    ]
    repo = FakeShotRepository(shots)
    out = SpyOutput()
    uc = ListShotsForProject(repo, out)
    uc.execute(ListShotsInput(project_id="  proj-1  "))
    assert repo.calls == ["proj-1"]
    assert len(out.shots_calls) == 1
    pid, got = out.shots_calls[0]
    assert pid == "proj-1"
    assert got[0].name == "Zebra"


def test_empty_project_id_errors() -> None:
    repo = FakeShotRepository([])
    out = SpyOutput()
    uc = ListShotsForProject(repo, out)
    uc.execute(ListShotsInput(project_id="   "))
    assert out.errors == ["project_id is required"]
    assert repo.calls == []


def test_repository_exception_surfaces_as_error() -> None:
    class BoomRepo:
        def list_shots(self, project_id: ProjectId) -> list[Shot]:
            raise RuntimeError("network down")

        def get_shot(self, project_id: ProjectId, shot_id: str) -> Shot | None:
            return None

        def update_shot_name(self, project_id: ProjectId, shot_id: str, new_name: str) -> None:
            pass

    out = SpyOutput()
    uc = ListShotsForProject(BoomRepo(), out)  # type: ignore[arg-type]
    uc.execute(ListShotsInput(project_id="p"))
    assert out.errors == ["network down"]
