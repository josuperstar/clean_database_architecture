from __future__ import annotations

import pytest

from business_entities import ShotStatus
from framework_and_drivers.integrations.shotgun.shotgun_client import _coerce_sg_status_list_field
from interface_adapters.repositories._status_mapping import normalize_vendor_status


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("fin", "fin"),
        ("  FIN  ", "FIN"),
        ({"code": "fin", "name": "Final"}, "fin"),
        ({"name": "Final"}, "Final"),
        ([{"code": "fin"}], "fin"),
        ({}, ""),
        (None, ""),
    ],
)
def test_coerce_sg_status_list_field(value: object, expected: str) -> None:
    assert _coerce_sg_status_list_field(value) == expected


def test_shotgun_fin_and_final_map_to_done() -> None:
    assert normalize_vendor_status("fin", flavor="shotgun") is ShotStatus.DONE
    assert normalize_vendor_status("Final", flavor="shotgun") is ShotStatus.DONE


def test_ftrack_display_labels_map_to_business_status() -> None:
    assert normalize_vendor_status("In Progress", flavor="ftrack") is ShotStatus.IN_PROGRESS
    assert normalize_vendor_status("Not Started", flavor="ftrack") is ShotStatus.READY_TO_START
    assert normalize_vendor_status("Approved", flavor="ftrack") is ShotStatus.DONE
    assert normalize_vendor_status("  not   started  ", flavor="ftrack") is ShotStatus.READY_TO_START


def test_approved_maps_to_done_for_all_flavors() -> None:
    for flavor in ("shotgun", "ftrack", "kitsu"):
        assert normalize_vendor_status("approved", flavor=flavor) is ShotStatus.DONE
