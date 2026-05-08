"""Map ftrack shot status labels (from API) to domain ``ShotStatus``.

All ftrack-specific strings live here so tracker changes stay localized to the ftrack path.
"""

from __future__ import annotations

import re
import unicodedata

from business_entities import ShotStatus


def _normalize_ftrack_status_token(raw: str) -> str:
    """Lowercase, collapse whitespace, normalize unicode spaces / hyphens for matching."""
    if not raw or not str(raw).strip():
        return ""
    t = unicodedata.normalize("NFKC", str(raw))
    for ch in ("\u00a0", "\u202f", "\u2009", "\u2007", "\ufeff"):
        t = t.replace(ch, " ")
    t = t.replace("_", " ").replace("-", " ")
    t = " ".join(t.split()).lower()
    return t


def _map_one_normalized_ftrack_label(r: str) -> ShotStatus | None:
    if not r:
        return None

    in_progress = {
        "ip",
        "in progress",
        "wip",
        "work in progress",
        "progress",
        "active",
        "in review",
        "internal review",
    }
    ready = {
        "rdy",
        "ready",
        "ready to start",
        "todo",
        "waiting",
        "not started",
        "notstarted",
        "wtg",
        "ns",  # common short for Not Started
        "nst",
    }
    done = {
        "fin",
        "done",
        "complete",
        "completed",
        "final",
        "closed",
        "ok",
        "approved",
        "approve",
        "accepted",
        "accept",
        "client approved",
        "final approved",
        "signed off",
        "delivered",
        "cmpt",
        "omitted",
        "omit",
        "retired",
        "cancelled",
        "canceled",
    }

    if r in in_progress:
        return ShotStatus.IN_PROGRESS
    if r in ready:
        return ShotStatus.READY_TO_START
    if r in done:
        return ShotStatus.DONE
    return None


def map_ftrack_shot_status(raw: str) -> ShotStatus:
    """
    Map ftrack-facing status text to ``ShotStatus``.

    ``raw`` may contain several fragments separated by ``|`` (see ftrack driver), each tried in order.
    """
    if not raw or not str(raw).strip():
        return ShotStatus.UNKNOWN

    for part in re.split(r"\s*\|\s*", str(raw)):
        token = _normalize_ftrack_status_token(part)
        if not token:
            continue
        mapped = _map_one_normalized_ftrack_label(token)
        if mapped is not None:
            return mapped

    return ShotStatus.UNKNOWN
