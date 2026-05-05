"""Shared source / project presets for Qt and web browser UI."""

from __future__ import annotations

# (label, tracking, fake_vendor when tracking is fake; else None)
BACKEND_OPTIONS: list[tuple[str, str, str | None]] = [
    ("Fake ShotGrid (in-memory)", "fake", "shotgun"),
    ("Fake ftrack (in-memory)", "fake", "ftrack"),
    ("Fake Kitsu (in-memory)", "fake", "kitsu"),
    ("ShotGrid / Shotgun (live API)", "shotgun", None),
    ("ftrack (live API)", "ftrack", None),
    ("Kitsu (live API)", "kitsu", None),
]

PROJECT_HINTS = [
    "Try project id: demo",
    "Try project id: ftrack-demo",
    "Try project id: kitsu-demo",
    "Enter your ShotGrid project id or name",
    "Enter your ftrack project id",
    "Enter your Kitsu project id",
]

FAKE_PROJECT_PRESETS: dict[tuple[str, str], list[str]] = {
    ("fake", "shotgun"): ["demo"],
    ("fake", "ftrack"): ["ftrack-demo"],
    ("fake", "kitsu"): ["kitsu-demo"],
}
