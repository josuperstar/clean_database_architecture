from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from framework_and_drivers.integrations.ftrack.ftrack_client import _resolve_ftrack_project


def test_resolve_ftrack_project_by_session_get() -> None:
    session = MagicMock()
    project = {"id": "abc", "children": []}
    session.get.return_value = project
    assert _resolve_ftrack_project(session, "abc") is project
    session.get.assert_called_once_with("Project", "abc")
    session.query.assert_not_called()


def test_resolve_ftrack_project_falls_back_to_name_query() -> None:
    session = MagicMock()
    session.get.return_value = None
    found = {"id": "uuid-1", "children": []}
    q1 = MagicMock()
    q1.all.return_value = [found]
    session.query.return_value = q1

    out = _resolve_ftrack_project(session, "sync")
    assert out is found
    session.query.assert_called_with('Project where name is "sync"')


def test_resolve_ftrack_project_not_found() -> None:
    session = MagicMock()
    session.get.return_value = None
    empty = MagicMock()
    empty.all.return_value = []
    session.query.return_value = empty

    with pytest.raises(RuntimeError, match="No ftrack Project found"):
        _resolve_ftrack_project(session, "nope")


def test_resolve_ftrack_project_ambiguous_name() -> None:
    session = MagicMock()
    session.get.return_value = None
    q = MagicMock()
    q.all.return_value = [{"id": "1"}, {"id": "2"}]
    session.query.return_value = q

    with pytest.raises(RuntimeError, match="Multiple ftrack projects"):
        _resolve_ftrack_project(session, "dup")
