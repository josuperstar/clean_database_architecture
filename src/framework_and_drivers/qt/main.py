from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from framework_and_drivers.composition.factory import build_list_shots_controller_qt
from interface_adapters.controllers.request_models import ListShotsRequestModel


def run_qt() -> int:
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Shots — Clean Architecture demo")

    project_input = QLineEdit()
    project_input.setPlaceholderText("Project id")

    load_btn = QPushButton("Load shots")
    output = QTextEdit()
    output.setReadOnly(True)

    def on_load() -> None:
        controller = build_list_shots_controller_qt(text_edit=output)
        controller.handle(ListShotsRequestModel(project_id=project_input.text()))

    load_btn.clicked.connect(on_load)

    row = QHBoxLayout()
    row.addWidget(QLabel("Project"))
    row.addWidget(project_input)
    row.addWidget(load_btn)

    layout = QVBoxLayout()
    layout.addLayout(row)
    layout.addWidget(output)
    window.setLayout(layout)
    window.resize(720, 480)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run_qt())
