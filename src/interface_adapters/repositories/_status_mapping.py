from __future__ import annotations

from business_entities import ShotStatus


def normalize_vendor_status(raw: str, *, flavor: str) -> ShotStatus:
    """Map vendor-specific status strings to `ShotStatus`. `flavor` is shotgun|ftrack|kitsu."""
    r = raw.strip().lower()
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
    }
    done = {
        "fin",  # ShotGrid / Shotgun status list short code (display often "Final")
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

    # flavor-specific short codes (examples)
    _ = flavor  # reserved for vendor-specific tables
    return ShotStatus.UNKNOWN
