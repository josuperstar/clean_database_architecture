"""Map ShotGrid / Shotgun ``sg_status_list``-style strings to ``ShotStatus``."""

from __future__ import annotations

from business_entities import ShotStatus


def map_shotgun_shot_status(raw: str) -> ShotStatus:
    r = " ".join(str(raw).strip().split()).lower()
    if not r:
        return ShotStatus.UNKNOWN

    in_progress = {
        "ip",
        "in progress",
        "in_progress",
        "wip",
        "work in progress",
        "progress",
        "active",
    }
    ready = {
        "rdy",
        "ready",
        "ready to start",
        "ready_to_start",
        "todo",
        "waiting",
        "not started",
        "not_started",
        "not-started",
    }
    done = {
        "fin",
        "done",
        "complete",
        "completed",
        "final",
        "closed",
        "ok",
    }

    if r in in_progress:
        return ShotStatus.IN_PROGRESS
    if r in ready:
        return ShotStatus.READY_TO_START
    if r in done:
        return ShotStatus.DONE
    return ShotStatus.UNKNOWN
