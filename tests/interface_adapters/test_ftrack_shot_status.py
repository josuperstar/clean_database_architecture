from __future__ import annotations

from business_entities import ShotStatus

from interface_adapters.repositories.ftrack_shot_status import map_ftrack_shot_status


def test_ftrack_common_display_labels() -> None:
    assert map_ftrack_shot_status("In Progress") is ShotStatus.IN_PROGRESS
    assert map_ftrack_shot_status("Not Started") is ShotStatus.READY_TO_START
    assert map_ftrack_shot_status("Approved") is ShotStatus.DONE


def test_ftrack_whitespace_and_unicode_spaces() -> None:
    assert map_ftrack_shot_status("  not   started  ") is ShotStatus.READY_TO_START
    # narrow no-break space between words (sometimes copied from ftrack UI)
    assert map_ftrack_shot_status("Not\u202fStarted") is ShotStatus.READY_TO_START


def test_ftrack_pipe_separated_prefers_first_matchable_fragment() -> None:
    assert map_ftrack_shot_status("internal_id | Not Started") is ShotStatus.READY_TO_START
    assert map_ftrack_shot_status("NS | Not Started") is ShotStatus.READY_TO_START


def test_ftrack_short_code_ns() -> None:
    assert map_ftrack_shot_status("NS") is ShotStatus.READY_TO_START
