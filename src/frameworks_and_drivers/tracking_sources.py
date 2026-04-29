from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TrackingSource:
    """Named backend wiring; same catalog for CLI, web, and Qt."""

    id: str
    label: str
    tracking: str
    fake_vendor: str | None
    seeded_project_hint: str | None


TRACKING_SOURCES: tuple[TrackingSource, ...] = (
    TrackingSource("fake_shotgun", "Fake ShotGrid (in-memory)", "fake", "shotgun", "demo"),
    TrackingSource("fake_ftrack", "Fake ftrack (in-memory)", "fake", "ftrack", "ftrack-demo"),
    TrackingSource("fake_kitsu", "Fake Kitsu (in-memory)", "fake", "kitsu", "kitsu-demo"),
    TrackingSource("shotgun", "ShotGrid (live API)", "shotgun", None, None),
    TrackingSource("ftrack", "ftrack (live API)", "ftrack", None, None),
    TrackingSource("kitsu", "Kitsu (live API)", "kitsu", None, None),
)


def tracking_source_ids() -> tuple[str, ...]:
    return tuple(s.id for s in TRACKING_SOURCES)


def normalize_source_id(raw: str) -> str:
    return raw.strip().lower().replace("-", "_")


def resolve_tracking_source(
    *,
    source: str | None,
    tracking: str | None,
    fake_vendor: str | None,
) -> tuple[str | None, str | None]:
    """Resolve factory ``tracking`` and ``fake_vendor``.

    When ``source`` is non-empty after strip, it picks a :data:`TRACKING_SOURCES` entry and
    ``tracking`` / ``fake_vendor`` are ignored. Otherwise those arguments pass through unchanged
    (factory/env defaults still apply).
    """
    if source is not None and source.strip():
        sid = normalize_source_id(source)
        for spec in TRACKING_SOURCES:
            if spec.id == sid:
                return spec.tracking, spec.fake_vendor
        allowed = ", ".join(tracking_source_ids())
        raise ValueError(f"Unknown source {source!r}; use one of: {allowed}")
    return tracking, fake_vendor
