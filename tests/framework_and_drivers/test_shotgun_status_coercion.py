from __future__ import annotations

import pytest

from business_entities import ShotStatus
from framework_and_drivers.integrations.shotgun.shotgun_client import _coerce_sg_status_list_field
from interface_adapters.repositories.shotgun_shot_status import map_shotgun_shot_status


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
    assert map_shotgun_shot_status("fin") is ShotStatus.DONE
    assert map_shotgun_shot_status("Final") is ShotStatus.DONE
