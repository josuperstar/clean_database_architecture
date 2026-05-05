"""Shared hex colors for ``ColorHint`` (Qt table, Qt HTML list, web UI)."""

from __future__ import annotations

from interface_adapters.view_models.list_shots_view_model import ColorHint

COLOR_HINT_HEX: dict[ColorHint, str] = {
    ColorHint.BLUE: "#2563eb",
    ColorHint.GREEN: "#16a34a",
    ColorHint.GRAY: "#6b7280",
    ColorHint.AMBER: "#d97706",
    ColorHint.NEUTRAL: "#111827",
}
