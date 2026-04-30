from __future__ import annotations

import re

from business_entities.shot import Shot


def infer_shot_name_first_token_from_shot(shot: Shot) -> str | None:
    """
    First segment of a valid shot display name is the shot's **sequence** (trimmed).

    Returns ``None`` when the shot has no sequence, so the caller must supply an override
    (CLI ``--project-code`` / Web ``project_code``) for the first token.
    """
    seq = (shot.sequence or "").strip()
    return seq or None


def assert_shot_display_name_matches_nomenclature(first_token: str, new_name: str) -> None:
    """
    Business rule: display name must be ``<first_token>_<digits>`` (e.g. ``SEQ01_01``).

    ``first_token`` is normally the shot's sequence name; matching is literal (regex-safe)
    so arbitrary sequence strings are allowed.
    """
    token = first_token.strip()
    name = new_name.strip()
    if not token:
        raise ValueError("First name segment (sequence) is required for nomenclature validation.")
    pattern = re.compile(rf"^{re.escape(token)}_\d+$")
    if not pattern.fullmatch(name):
        raise ValueError(
            f"Shot name must match {token!r}_<digits> (e.g. {token}_01). Got {name!r}."
        )
