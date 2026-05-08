from __future__ import annotations

from business_entities import ShotStatus


def normalize_vendor_status(raw: str, *, flavor: str) -> ShotStatus:
    """Map vendor-specific status strings to `ShotStatus`. `flavor` is shotgun|ftrack|kitsu."""
    r = " ".join(raw.strip().split()).lower()
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
        "fin",  # ShotGrid / Shotgun status list short code (display often "Final")
        "done",
        "complete",
        "completed",
        "final",
        "closed",
        "ok",
        # ftrack (and similar) review / sign-off labels → DONE (rename blocked, gray in UI)
        "approved",
        "approve",
        "accepted",
        "accept",
        "client approved",
        "client_approved",
        "final approved",
        "final_approved",
        "signed off",
        "signed_off",
        "delivered",
    }

    if r in in_progress:
        return ShotStatus.IN_PROGRESS
    if r in ready:
        return ShotStatus.READY_TO_START
    if r in done:
        return ShotStatus.DONE

    if flavor == "ftrack":
        # Optional short codes from common ftrack schemas (add yours if still UNKNOWN)
        ftrack_in_progress = {
            "in review",
            "in_review",
            "internal review",
            "internal_review",
        }
        ftrack_ready = {"wtg"}
        ftrack_done = {
            "cmpt",
            "omitted",
            "omit",
            "retired",
            "cancelled",
            "canceled",
        }
        if r in ftrack_in_progress:
            return ShotStatus.IN_PROGRESS
        if r in ftrack_ready:
            return ShotStatus.READY_TO_START
        if r in ftrack_done:
            return ShotStatus.DONE

    return ShotStatus.UNKNOWN
