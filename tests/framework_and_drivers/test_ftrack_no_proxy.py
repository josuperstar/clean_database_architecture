from __future__ import annotations

import os

import pytest

from framework_and_drivers.integrations.ftrack.ftrack_client import ensure_ftrack_host_bypasses_proxy


def test_ensure_ftrack_host_bypasses_proxy_appends_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NO_PROXY", raising=False)
    monkeypatch.delenv("no_proxy", raising=False)
    monkeypatch.setenv("FTRACK_AUTO_NO_PROXY", "1")
    ensure_ftrack_host_bypasses_proxy("https://pitch-black.ftrackapp.com/")
    assert os.environ["NO_PROXY"] == "pitch-black.ftrackapp.com"
    assert os.environ["no_proxy"] == "pitch-black.ftrackapp.com"


def test_ensure_ftrack_host_bypasses_proxy_extends_existing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "localhost,127.0.0.1")
    monkeypatch.setenv("no_proxy", "localhost")
    monkeypatch.setenv("FTRACK_AUTO_NO_PROXY", "1")
    ensure_ftrack_host_bypasses_proxy("https://example.ftrackapp.com/")
    assert "example.ftrackapp.com" in os.environ["NO_PROXY"]
    assert "example.ftrackapp.com" in os.environ["no_proxy"]


def test_ensure_ftrack_host_bypasses_proxy_respects_disable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NO_PROXY", raising=False)
    monkeypatch.delenv("no_proxy", raising=False)
    monkeypatch.setenv("FTRACK_AUTO_NO_PROXY", "0")
    ensure_ftrack_host_bypasses_proxy("https://pitch-black.ftrackapp.com/")
    assert "NO_PROXY" not in os.environ
    assert "no_proxy" not in os.environ
