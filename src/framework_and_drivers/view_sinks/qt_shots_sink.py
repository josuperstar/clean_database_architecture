from __future__ import annotations

from interface_adapters.view_models.list_shots_view_model import ColorHint, ListShotsViewModel

_HTML = {
    ColorHint.BLUE: "#2563eb",
    ColorHint.GREEN: "#16a34a",
    ColorHint.GRAY: "#6b7280",
    ColorHint.AMBER: "#d97706",
    ColorHint.NEUTRAL: "#111827",
}


class QtShotsViewSink:
    def __init__(self, text_edit: object) -> None:
        from PySide6.QtWidgets import QTextEdit  # noqa: PLC0415

        if not isinstance(text_edit, QTextEdit):
            raise TypeError("text_edit must be a PySide6.QtWidgets.QTextEdit")
        self._text = text_edit

    def render(self, view_model: ListShotsViewModel) -> None:
        parts: list[str] = [f"<h3>Project {view_model.project_id}</h3><ul>"]
        for row in view_model.rows:
            color = _HTML.get(row.color_hint, _HTML[ColorHint.NEUTRAL])
            parts.append(
                f"<li style='color:{color}'><b>{row.name}</b> — {row.status_label}</li>"
            )
        parts.append("</ul>")
        self._text.setHtml("".join(parts))

    def render_error(self, message: str) -> None:
        self._text.setHtml(f"<p style='color:#b91c1c'>{message}</p>")
