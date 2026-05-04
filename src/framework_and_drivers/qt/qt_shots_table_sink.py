from __future__ import annotations

from interface_adapters.view_models.color_hint_theme import COLOR_HINT_HEX
from interface_adapters.view_models.list_shots_view_model import ColorHint, ListShotsViewModel


class QtShotsTableSink:
    """Fills a ``QTableWidget`` with one row per shot; ``shot_id`` is on column 0 ``UserRole``."""

    _HEADERS = ("Name", "Sequence", "Status")

    def __init__(self, table: object) -> None:
        from PySide6.QtWidgets import QTableWidget  # noqa: PLC0415

        if not isinstance(table, QTableWidget):
            raise TypeError("table must be a PySide6.QtWidgets.QTableWidget")
        self._table = table

    def render(self, view_model: ListShotsViewModel) -> None:
        from PySide6.QtCore import Qt  # noqa: PLC0415
        from PySide6.QtGui import QBrush, QColor  # noqa: PLC0415
        from PySide6.QtWidgets import QTableWidgetItem  # noqa: PLC0415

        qt_fg = {hint: QColor(hex_) for hint, hex_ in COLOR_HINT_HEX.items()}

        self._table.clearSpans()
        self._table.setColumnCount(len(self._HEADERS))
        self._table.setHorizontalHeaderLabels(list(self._HEADERS))
        self._table.setRowCount(len(view_model.rows))

        for i, row in enumerate(view_model.rows):
            color = qt_fg.get(row.color_hint, qt_fg[ColorHint.NEUTRAL])
            brush = QBrush(color)

            name_item = QTableWidgetItem(row.name)
            name_item.setData(Qt.ItemDataRole.UserRole, row.shot_id)
            name_item.setForeground(brush)
            self._table.setItem(i, 0, name_item)

            seq_item = QTableWidgetItem(row.sequence or "—")
            seq_item.setForeground(brush)
            self._table.setItem(i, 1, seq_item)

            status_item = QTableWidgetItem(row.status_label)
            status_item.setForeground(brush)
            self._table.setItem(i, 2, status_item)

        self._table.resizeColumnsToContents()
        self._table.clearSelection()

    def render_error(self, message: str) -> None:
        from PySide6.QtGui import QBrush, QColor  # noqa: PLC0415
        from PySide6.QtWidgets import QTableWidgetItem  # noqa: PLC0415

        self._table.clearSpans()
        self._table.setColumnCount(1)
        self._table.setHorizontalHeaderLabels(["Error"])
        self._table.setRowCount(1)
        err = QTableWidgetItem(message)
        err.setForeground(QBrush(QColor("#b91c1c")))
        self._table.setItem(0, 0, err)
        self._table.clearSelection()
