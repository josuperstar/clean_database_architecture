from __future__ import annotations

from business_entities import ProjectId, Shot, ShotStatus
from use_cases.update_shot_name.input import UpdateShotNameInput
from use_cases.update_shot_name.update_shot_name import UpdateShotName


class MutableShotRepository:
    def __init__(self, by_project: dict[str, dict[str, Shot]]) -> None:
        self._by_project = {k: dict(v) for k, v in by_project.items()}

    def list_shots(self, project_id: ProjectId) -> list[Shot]:
        return list(self._by_project.get(str(project_id), {}).values())

    def get_shot(self, project_id: ProjectId, shot_id: str) -> Shot | None:
        return self._by_project.get(str(project_id), {}).get(shot_id)

    def update_shot_name(self, project_id: ProjectId, shot_id: str, new_name: str) -> None:
        d = self._by_project[str(project_id)]
        old = d[shot_id]
        d[shot_id] = Shot(
            id=old.id,
            name=new_name,
            code=new_name,
            sequence=old.sequence,
            status=old.status,
        )


class SpyRenameOutput:
    def __init__(self) -> None:
        self.ok: list[tuple[str, str, str]] = []
        self.errors: list[str] = []

    def present_renamed(self, project_id: str, shot_id: str, new_name: str) -> None:
        self.ok.append((project_id, shot_id, new_name))

    def present_error(self, message: str) -> None:
        self.errors.append(message)


def _repo_with_ready_shot() -> MutableShotRepository:
    shot = Shot(
        id="3",
        name="SEQ02_30",
        code="SEQ02_30",
        sequence="SEQ02",
        status=ShotStatus.READY_TO_START,
    )
    return MutableShotRepository({"demo": {"3": shot}})


def test_rename_success_updates_repo() -> None:
    repo = _repo_with_ready_shot()
    out = SpyRenameOutput()
    uc = UpdateShotName(repo, out)
    uc.execute(
        UpdateShotNameInput(
            project_id="demo",
            shot_id="3",
            new_name="SEQ02_42",
            project_code="",
        )
    )
    assert out.ok == [("demo", "3", "SEQ02_42")]
    assert out.errors == []
    assert repo.get_shot(ProjectId("demo"), "3") is not None
    updated = repo.get_shot(ProjectId("demo"), "3")
    assert updated is not None
    assert updated.name == "SEQ02_42"
    assert updated.code == "SEQ02_42"


def test_rename_explicit_project_code_overrides_inference() -> None:
    repo = _repo_with_ready_shot()
    out = SpyRenameOutput()
    uc = UpdateShotName(repo, out)
    uc.execute(
        UpdateShotNameInput(
            project_id="demo",
            shot_id="3",
            new_name="ZZZ_01",
            project_code="ZZZ",
        )
    )
    assert out.ok == [("demo", "3", "ZZZ_01")]
    assert out.errors == []


def test_rename_blocked_when_done() -> None:
    shot = Shot(
        id="2",
        name="SEQ01_20",
        code="SEQ01_20",
        sequence="SEQ01",
        status=ShotStatus.DONE,
    )
    repo = MutableShotRepository({"demo": {"2": shot}})
    out = SpyRenameOutput()
    uc = UpdateShotName(repo, out)
    uc.execute(
        UpdateShotNameInput(
            project_id="demo",
            shot_id="2",
            new_name="SEQ01_99",
            project_code="",
        )
    )
    assert out.ok == []
    assert "in progress or done" in out.errors[0].lower()


def test_rename_blocked_when_in_progress() -> None:
    shot = Shot(
        id="1",
        name="SEQ01_10",
        code="SEQ01_10",
        sequence="SEQ01",
        status=ShotStatus.IN_PROGRESS,
    )
    repo = MutableShotRepository({"demo": {"1": shot}})
    out = SpyRenameOutput()
    uc = UpdateShotName(repo, out)
    uc.execute(
        UpdateShotNameInput(
            project_id="demo",
            shot_id="1",
            new_name="SEQ01_01",
            project_code="",
        )
    )
    assert out.ok == []
    assert len(out.errors) == 1
    assert "in progress or done" in out.errors[0].lower()
    s = repo.get_shot(ProjectId("demo"), "1")
    assert s is not None
    assert s.name == "SEQ01_10"
    assert s.code == "SEQ01_10"


def test_rename_rejected_bad_nomenclature() -> None:
    repo = _repo_with_ready_shot()
    out = SpyRenameOutput()
    uc = UpdateShotName(repo, out)
    uc.execute(
        UpdateShotNameInput(
            project_id="demo",
            shot_id="3",
            new_name="wrong_name",
            project_code="",
        )
    )
    assert out.ok == []
    assert out.errors
    s = repo.get_shot(ProjectId("demo"), "3")
    assert s is not None
    assert s.name == "SEQ02_30"
    assert s.code == "SEQ02_30"


def test_rename_fails_when_project_code_cannot_be_inferred() -> None:
    shot = Shot(
        id="x",
        name="No pattern here",
        code="No pattern here",
        sequence=None,
        status=ShotStatus.READY_TO_START,
    )
    repo = MutableShotRepository({"demo": {"x": shot}})
    out = SpyRenameOutput()
    uc = UpdateShotName(repo, out)
    uc.execute(
        UpdateShotNameInput(
            project_id="demo",
            shot_id="x",
            new_name="ANY_01",
            project_code="",
        )
    )
    assert out.ok == []
    assert "Could not infer the first name segment" in out.errors[0]


def test_rename_missing_shot() -> None:
    repo = _repo_with_ready_shot()
    out = SpyRenameOutput()
    uc = UpdateShotName(repo, out)
    uc.execute(
        UpdateShotNameInput(
            project_id="demo",
            shot_id="99",
            new_name="SEQ02_01",
            project_code="",
        )
    )
    assert "No shot" in out.errors[0]
