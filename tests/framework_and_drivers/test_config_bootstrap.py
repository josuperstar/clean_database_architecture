from __future__ import annotations

import os
from pathlib import Path

import pytest

from framework_and_drivers.composition import config_bootstrap


def test_parse_env_style_ini(tmp_path: Path) -> None:
    p = tmp_path / "config.ini"
    p.write_text(
        "# c\n"
        "TRACKING_BACKEND=shotgun\n"
        " EMPTY = ignored \n"
        "QUOTED='x y'\n"
        "BLANK=\n",
        encoding="utf-8",
    )
    d = config_bootstrap._parse_env_style_ini(p)
    assert d["TRACKING_BACKEND"] == "shotgun"
    assert d["QUOTED"] == "x y"
    assert d["BLANK"] == ""


def test_bootstrap_setdefault_respects_existing_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    p = tmp_path / "config.ini"
    p.write_text("TRACKING_BACKEND=kitsu\nFAKE_VENDOR=ftrack\n", encoding="utf-8")
    monkeypatch.setenv("TRACKING_BACKEND", "fake")
    monkeypatch.delenv("FAKE_VENDOR", raising=False)
    monkeypatch.setenv(config_bootstrap._ENV_CONFIG_PATH, str(p))

    assert os.environ["TRACKING_BACKEND"] == "fake"
    loaded = config_bootstrap.bootstrap_config_from_ini()
    assert loaded == p.resolve()
    assert os.environ["TRACKING_BACKEND"] == "fake"
    assert os.environ["FAKE_VENDOR"] == "ftrack"
