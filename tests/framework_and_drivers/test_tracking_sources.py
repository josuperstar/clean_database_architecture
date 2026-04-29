from __future__ import annotations

import pytest

from framework_and_drivers.tracking_sources import (
    normalize_source_id,
    resolve_tracking_source,
    tracking_source_ids,
)


def test_resolve_source_overrides_tracking_and_vendor() -> None:
    t, fv = resolve_tracking_source(
        source="fake_ftrack", tracking="shotgun", fake_vendor="shotgun"
    )
    assert t == "fake"
    assert fv == "ftrack"


def test_resolve_hyphenated_source_id() -> None:
    t, fv = resolve_tracking_source(source="fake-kitsu", tracking=None, fake_vendor=None)
    assert t == "fake"
    assert fv == "kitsu"


def test_resolve_pass_through_when_source_empty() -> None:
    t, fv = resolve_tracking_source(source=None, tracking="fake", fake_vendor="shotgun")
    assert t == "fake"
    assert fv == "shotgun"
    t2, fv2 = resolve_tracking_source(source="   ", tracking=None, fake_vendor=None)
    assert t2 is None
    assert fv2 is None


def test_resolve_unknown_source() -> None:
    with pytest.raises(ValueError, match="Unknown source"):
        resolve_tracking_source(source="nope", tracking=None, fake_vendor=None)


def test_normalize_source_id() -> None:
    assert normalize_source_id("  Fake-Shotgun ") == "fake_shotgun"


def test_catalog_ids_unique() -> None:
    ids = tracking_source_ids()
    assert len(ids) == len(set(ids))