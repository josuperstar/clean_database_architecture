from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ColorHint(str, Enum):
    """Semantic color tokens; UI sinks map these to ANSI/CSS/Qt."""

    BLUE = "blue"
    GREEN = "green"
    GRAY = "gray"
    AMBER = "amber"
    NEUTRAL = "neutral"


class FontEmphasis(str, Enum):
    NORMAL = "normal"
    STRONG = "strong"


@dataclass(frozen=True, slots=True)
class ShotRowViewModel:
    shot_id: str
    name: str
    code: str
    sequence: str | None
    status_label: str
    color_hint: ColorHint
    font_emphasis: FontEmphasis = FontEmphasis.NORMAL


@dataclass(frozen=True, slots=True)
class ListShotsViewModel:
    project_id: str
    rows: tuple[ShotRowViewModel, ...]
