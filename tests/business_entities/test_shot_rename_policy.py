from __future__ import annotations

import pytest

from business_entities import (
    Shot,
    ShotStatus,
    assert_shot_display_name_matches_nomenclature,
    infer_shot_name_first_token_from_shot,
)


def test_nomenclature_accepts_sequence_and_digits() -> None:
    assert_shot_display_name_matches_nomenclature("SEQ01", "SEQ01_01")
    assert_shot_display_name_matches_nomenclature("ACME", "ACME_999")


def test_nomenclature_rejects_wrong_first_token() -> None:
    with pytest.raises(ValueError, match="must match"):
        assert_shot_display_name_matches_nomenclature("SEQ01", "OTHER_01")


def test_nomenclature_rejects_non_numeric_suffix() -> None:
    with pytest.raises(ValueError, match="must match"):
        assert_shot_display_name_matches_nomenclature("SEQ01", "SEQ01_1a")


def test_nomenclature_rejects_empty_first_token() -> None:
    with pytest.raises(ValueError, match="First name segment"):
        assert_shot_display_name_matches_nomenclature("", "ANY_01")


def test_nomenclature_first_token_may_include_regex_special_chars() -> None:
    assert_shot_display_name_matches_nomenclature("MY.SEQ", "MY.SEQ_1")


def test_infer_first_token_from_sequence() -> None:
    s = Shot("1", "SEQ01_01", "SEQ01_01", "SEQ01", ShotStatus.READY_TO_START)
    assert infer_shot_name_first_token_from_shot(s) == "SEQ01"


def test_infer_strips_sequence_whitespace() -> None:
    s = Shot("1", "X", "X", "  Anim  ", ShotStatus.READY_TO_START)
    assert infer_shot_name_first_token_from_shot(s) == "Anim"


def test_infer_returns_none_when_sequence_missing() -> None:
    s = Shot("1", "X", "X", None, ShotStatus.READY_TO_START)
    assert infer_shot_name_first_token_from_shot(s) is None


def test_shot_can_rename_by_status() -> None:
    ready = Shot("1", "A", "A", "S", ShotStatus.READY_TO_START)
    assert ready.can_rename() is True
    ip = Shot("2", "B", "B", "S", ShotStatus.IN_PROGRESS)
    assert ip.can_rename() is False
    done = Shot("3", "C", "C", "S", ShotStatus.DONE)
    assert done.can_rename() is False
