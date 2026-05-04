from __future__ import annotations

import sys
from typing import Any

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from framework_and_drivers.composition.factory import (
    build_list_shots_controller_qt,
    build_update_shot_name_controller_qt,
)
from framework_and_drivers.tracking_presets import (
    BACKEND_OPTIONS,
    FAKE_PROJECT_PRESETS,
    PROJECT_HINTS,
)
from interface_adapters.controllers.request_models import ListShotsRequestModel, UpdateShotNameRequestModel


def _backend_from_combo(combo: QComboBox) -> tuple[str, str | None]:
    data: Any = combo.currentData()
    if not isinstance(data, tuple) or len(data) != 2:
        return "fake", "shotgun"
    t, fv = data[0], data[1]
    return str(t), (str(fv) if fv is not None else None)


def _selected_shot_id(table: QTableWidget) -> str | None:
    row = table.currentRow()
    if row < 0:
        return None
    item = table.item(row, 0)
    if item is None:
        return None
    sid = item.data(Qt.ItemDataRole.UserRole)
    return str(sid) if sid is not None else None


def _prompt_new_shot_name(parent: QWidget) -> str | None:
    """Returns trimmed new name or ``None`` if cancelled."""
    d = QDialog(parent)
    d.setWindowTitle("Rename shot")
    name_edit = QLineEdit()
    name_edit.setPlaceholderText("e.g. SEQ02_01 — must match <sequence>_<digits> (sequence from shot)")
    form = QFormLayout()
    form.addRow("New name", name_edit)
    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    buttons.accepted.connect(d.accept)
    buttons.rejected.connect(d.reject)
    outer = QVBoxLayout(d)
    outer.addLayout(form)
    outer.addWidget(buttons)
    if d.exec() != QDialog.DialogCode.Accepted:
        return None
    return name_edit.text().strip()


def run_qt() -> int:
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Shots — Clean Architecture demo")

    source_combo = QComboBox()
    for label, tracking, fake_vendor in BACKEND_OPTIONS:
        source_combo.addItem(label, (tracking, fake_vendor))

    project_hint = QLabel(PROJECT_HINTS[0])
    project_hint.setWordWrap(True)
    project_hint.setStyleSheet("color: #4b5563; font-size: 11px;")

    project_combo = QComboBox()
    project_combo.setEditable(True)
    project_combo.setMinimumContentsLength(18)
    project_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

    def _project_id() -> str:
        return project_combo.currentText().strip()

    def refresh_project_combo() -> None:
        idx = source_combo.currentIndex()
        project_combo.blockSignals(True)
        project_combo.clear()
        tracking, fake_vendor = _backend_from_combo(source_combo)
        fv = fake_vendor or ""
        presets = FAKE_PROJECT_PRESETS.get((tracking, fv), [])
        if presets:
            for pid in presets:
                project_combo.addItem(pid)
            project_combo.setCurrentIndex(0)
        else:
            project_combo.setEditText("")
        project_combo.blockSignals(False)
        le = project_combo.lineEdit()
        if le is not None:
            if 0 <= idx < len(PROJECT_HINTS):
                le.setPlaceholderText(PROJECT_HINTS[idx])
            else:
                le.setPlaceholderText("Project id")

    def on_source_changed(_: int) -> None:
        project_hint.setText(PROJECT_HINTS[source_combo.currentIndex()])
        refresh_project_combo()

    source_combo.currentIndexChanged.connect(on_source_changed)
    refresh_project_combo()

    load_btn = QPushButton("Load shots")

    shot_table = QTableWidget()
    shot_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    shot_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    shot_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    shot_table.setAlternatingRowColors(True)

    rename_status = QLabel("")
    rename_status.setWordWrap(True)

    selected_shot_label = QLabel(
        "Load shots, then select a row (or right-click a row for Rename this shot...)."
    )
    selected_shot_label.setWordWrap(True)

    new_name_input = QLineEdit()
    new_name_input.setPlaceholderText("New name, e.g. SEQ02_99 (sequence from selected shot)")

    rename_btn = QPushButton("Rename selected shot")

    def on_load() -> None:
        tracking, fake_vendor = _backend_from_combo(source_combo)
        controller = build_list_shots_controller_qt(
            shot_list_widget=shot_table,
            tracking=tracking,
            fake_vendor=fake_vendor,
        )
        controller.handle(ListShotsRequestModel(project_id=_project_id()))
        update_selection_label()

    def update_selection_label() -> None:
        sid = _selected_shot_id(shot_table)
        if sid is None:
            selected_shot_label.setText(
                "No shot selected. Click a row in the table, or right-click a row for the rename menu."
            )
            rename_btn.setEnabled(False)
            return
        row = shot_table.currentRow()
        name_item = shot_table.item(row, 0)
        name = name_item.text() if name_item else "?"
        selected_shot_label.setText(f"Selected: {name}  (id: {sid})")
        rename_btn.setEnabled(True)

    shot_table.itemSelectionChanged.connect(update_selection_label)

    def run_rename_for_shot(shot_id: str, new_name: str, *, project_code: str = "") -> None:
        tracking, fake_vendor = _backend_from_combo(source_combo)
        controller = build_update_shot_name_controller_qt(
            status_label=rename_status,
            tracking=tracking,
            fake_vendor=fake_vendor,
        )
        controller.handle(
            UpdateShotNameRequestModel(
                project_id=_project_id(),
                shot_id=shot_id,
                new_name=new_name,
                project_code=project_code,
            )
        )
        on_load()

    def on_rename_clicked() -> None:
        sid = _selected_shot_id(shot_table)
        if not sid:
            rename_status.setText("Select a shot in the table first.")
            rename_status.setStyleSheet("color: #b91c1c;")
            return
        new_name = new_name_input.text().strip()
        if not new_name:
            rename_status.setText("Enter a new name (e.g. SEQ02_01).")
            rename_status.setStyleSheet("color: #b91c1c;")
            return
        run_rename_for_shot(sid, new_name)

    rename_btn.clicked.connect(on_rename_clicked)

    def on_table_context_menu(pos: QPoint) -> None:
        idx = shot_table.indexAt(pos)
        if not idx.isValid():
            return
        row = idx.row()
        item0 = shot_table.item(row, 0)
        if item0 is None:
            return
        shot_id = item0.data(Qt.ItemDataRole.UserRole)
        if shot_id is None:
            return
        shot_table.selectRow(row)
        menu = QMenu(shot_table)
        act = menu.addAction("Rename this shot...")
        chosen = menu.exec(shot_table.viewport().mapToGlobal(pos))
        if chosen != act:
            return
        new_name = _prompt_new_shot_name(window)
        if new_name is None:
            return
        if not new_name:
            rename_status.setText("Rename cancelled: new name is required.")
            rename_status.setStyleSheet("color: #b91c1c;")
            return
        run_rename_for_shot(str(shot_id), new_name)

    shot_table.customContextMenuRequested.connect(on_table_context_menu)

    load_btn.clicked.connect(on_load)

    rename_form = QFormLayout()
    rename_form.addRow("New name", new_name_input)

    rename_box = QGroupBox(
        "Rename selected shot (first segment defaults to shot sequence; name must be <sequence>_<digits>; "
        "blocked if in progress or done)"
    )
    rename_inner = QVBoxLayout()
    rename_inner.addWidget(selected_shot_label)
    rename_inner.addLayout(rename_form)
    rename_inner.addWidget(rename_btn)
    rename_inner.addWidget(rename_status)
    rename_box.setLayout(rename_inner)

    top = QHBoxLayout()
    top.addWidget(QLabel("Source"))
    top.addWidget(source_combo, stretch=1)

    row = QHBoxLayout()
    row.addWidget(QLabel("Project"))
    row.addWidget(project_combo, stretch=1)
    row.addWidget(load_btn)

    layout = QVBoxLayout()
    layout.addLayout(top)
    layout.addWidget(project_hint)
    layout.addLayout(row)
    layout.addWidget(shot_table, stretch=1)
    layout.addWidget(rename_box)
    window.setLayout(layout)
    window.resize(820, 560)
    rename_btn.setEnabled(False)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run_qt())
