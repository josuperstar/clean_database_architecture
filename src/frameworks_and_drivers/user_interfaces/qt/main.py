from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from frameworks_and_drivers.env_bootstrap import load_application_dotenv
from frameworks_and_drivers.composition.factory import build_list_shots_controller_qt
from frameworks_and_drivers.tracking_sources import TRACKING_SOURCES
from interface_adapters.controllers.request_models import ListShotsRequestModel


def run_qt() -> int:
    load_application_dotenv()
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Shots — Clean Architecture demo")

    source_combo = QComboBox()
    for spec in TRACKING_SOURCES:
        source_combo.addItem(spec.label)

    source_hint = QLabel()
    source_hint.setWordWrap(True)
    source_hint.setTextFormat(Qt.TextFormat.RichText)

    project_input = QLineEdit()
    project_input.setPlaceholderText("Project id")

    load_btn = QPushButton("Load shots")
    output = QTextEdit()
    output.setReadOnly(True)

    def _refresh_source_hint() -> None:
        spec = TRACKING_SOURCES[source_combo.currentIndex()]
        if spec.seeded_project_hint:
            source_hint.setText(
                f"Seeded demo project for this source: <b>{spec.seeded_project_hint}</b>"
            )
        else:
            source_hint.setText(
                "Live API: use a real project id from that system (configure credentials in <code>.env</code>)."
            )

    def on_load() -> None:
        spec = TRACKING_SOURCES[source_combo.currentIndex()]
        controller = build_list_shots_controller_qt(
            text_edit=output,
            tracking=spec.tracking,
            fake_vendor=spec.fake_vendor,
        )
        controller.handle(ListShotsRequestModel(project_id=project_input.text()))

    source_combo.currentIndexChanged.connect(lambda _i: _refresh_source_hint())
    load_btn.clicked.connect(on_load)

    source_row = QHBoxLayout()
    source_row.addWidget(QLabel("Source"))
    source_row.addWidget(source_combo, stretch=1)

    project_row = QHBoxLayout()
    project_row.addWidget(QLabel("Project"))
    project_row.addWidget(project_input)
    project_row.addWidget(load_btn)

    layout = QVBoxLayout()
    layout.addLayout(source_row)
    layout.addWidget(source_hint)
    layout.addLayout(project_row)
    layout.addWidget(output)
    window.setLayout(layout)
    window.resize(720, 480)
    _refresh_source_hint()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run_qt())
