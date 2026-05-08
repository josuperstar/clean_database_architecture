from __future__ import annotations

from unittest.mock import MagicMock

from framework_and_drivers.integrations.ftrack.ftrack_client import (
    _query_shots_for_ftrack_project,
    _ftrack_shot_to_raw_row,
)


def test_query_shots_for_ftrack_project_uses_project_id() -> None:
    session = MagicMock()
    project = {"id": "proj-uuid-1"}
    shot = {
        "entity_type": "Shot",
        "id": "shot-1",
        "name": "SH010",
        "status": {"name": "In progress"},
        "parent": {"entity_type": "Sequence", "name": "SEQ_A"},
    }
    qm = MagicMock()
    qm.all.return_value = [shot]
    session.query.return_value = qm

    rows = _query_shots_for_ftrack_project(session, project)
    session.query.assert_called_once_with('Shot where project.id is "proj-uuid-1"')
    assert len(rows) == 1
    assert rows[0].external_id == "shot-1"
    assert rows[0].name == "SH010"
    assert rows[0].sequence == "SEQ_A"
    assert rows[0].status_vendor == "In progress"


def test_ftrack_shot_to_raw_row_minimal() -> None:
    row = _ftrack_shot_to_raw_row(
        {"id": "s", "name": "X", "status": None, "parent": None},
    )
    assert row.external_id == "s"
    assert row.sequence is None
