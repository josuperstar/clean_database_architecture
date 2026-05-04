from __future__ import annotations

from fastapi.testclient import TestClient

from framework_and_drivers.web.app import app


def test_root_serves_browser_ui_with_shared_color_theme() -> None:
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")
    body = r.text
    assert 'id="boot-json"' in body
    assert "table-scroll" in body
    assert "Fake ShotGrid (in-memory)" in body
    assert "#2563eb" in body  # ColorHint.BLUE in COLOR_HINT_HEX (same as Qt)


def test_rename_shot_ok_fake_shotgun_inferred_prefix() -> None:
    client = TestClient(app)
    r = client.post(
        "/shots/rename?tracking=fake&fake_vendor=shotgun",
        json={
            "project_id": "demo",
            "shot_id": "3",
            "new_name": "SEQ02_07",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "Renamed shot" in data["message"]


def test_rename_shot_ok_with_explicit_project_code_override() -> None:
    client = TestClient(app)
    r = client.post(
        "/shots/rename?tracking=fake&fake_vendor=shotgun",
        json={
            "project_id": "demo",
            "shot_id": "3",
            "new_name": "WEB_01",
            "project_code": "WEB",
        },
    )
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_rename_shot_rejected_bad_nomenclature() -> None:
    client = TestClient(app)
    r = client.post(
        "/shots/rename?tracking=fake&fake_vendor=shotgun",
        json={
            "project_id": "demo",
            "shot_id": "3",
            "new_name": "not_valid",
        },
    )
    assert r.status_code == 400
    assert "error" in r.json()


def test_rename_shot_blocked_in_progress() -> None:
    client = TestClient(app)
    r = client.post(
        "/shots/rename?tracking=fake&fake_vendor=shotgun",
        json={
            "project_id": "demo",
            "shot_id": "1",
            "new_name": "OPN_02",
        },
    )
    assert r.status_code == 400
    assert "in progress or done" in r.json()["error"].lower()
