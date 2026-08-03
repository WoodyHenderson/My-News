from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStyle,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"


def discover_html_outputs(output_dir: Path) -> list[Path]:
    """Return generated HTML files with the most recently modified first."""
    if not output_dir.is_dir():
        return []

    outputs = [
        path
        for path in output_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".html"
    ]
    return sorted(outputs, key=lambda path: (path.stat().st_mtime, path.name), reverse=True)


class MainWindow(QMainWindow):
    def __init__(self, output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
        super().__init__()
        self.output_dir = output_dir

        self.setObjectName("mainWindow")
        self.setWindowTitle("My News")
        self.setMinimumSize(820, 560)
        self.resize(1040, 680)

        self._build_ui()
        self._apply_styles()
        self.refresh_outputs()

    def _build_ui(self) -> None:
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        page_layout = QVBoxLayout(central_widget)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        masthead = QWidget()
        masthead.setObjectName("masthead")
        masthead_layout = QVBoxLayout(masthead)
        masthead_layout.setContentsMargins(64, 34, 64, 30)
        masthead_layout.setSpacing(7)

        edition_label = QLabel(date.today().strftime("%A / %B %d, %Y").upper())
        edition_label.setObjectName("editionLabel")
        masthead_layout.addWidget(edition_label)

        title_row = QHBoxLayout()
        title_row.setSpacing(20)

        title = QLabel("My News")
        title.setObjectName("mastheadTitle")
        title_row.addWidget(title)
        title_row.addStretch()

        publication_label = QLabel("PERSONAL DAILY DIGEST")
        publication_label.setObjectName("publicationLabel")
        title_row.addWidget(publication_label, alignment=Qt.AlignmentFlag.AlignBottom)
        masthead_layout.addLayout(title_row)
        page_layout.addWidget(masthead)

        accent_rule = QFrame()
        accent_rule.setObjectName("accentRule")
        accent_rule.setFixedHeight(5)
        page_layout.addWidget(accent_rule)

        content = QWidget()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(64, 52, 64, 40)
        content_layout.setSpacing(0)

        section_label = QLabel("DIGEST LIBRARY")
        section_label.setObjectName("sectionLabel")
        content_layout.addWidget(section_label)

        section_title = QLabel("Today’s reading, ready when you are.")
        section_title.setObjectName("sectionTitle")
        section_title.setWordWrap(True)
        content_layout.addWidget(section_title)

        selector_label = QLabel("EDITION")
        selector_label.setObjectName("fieldLabel")
        content_layout.addSpacing(34)
        content_layout.addWidget(selector_label)

        selector_row = QHBoxLayout()
        selector_row.setSpacing(10)

        self.output_selector = QComboBox()
        self.output_selector.setObjectName("outputSelector")
        self.output_selector.setMinimumHeight(52)
        self.output_selector.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        selector_row.addWidget(self.output_selector)

        refresh_button = QToolButton()
        refresh_button.setObjectName("refreshButton")
        refresh_button.setToolTip("Refresh digest list")
        refresh_button.setAccessibleName("Refresh digest list")
        refresh_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        )
        refresh_button.setIconSize(QSize(20, 20))
        refresh_button.setFixedSize(52, 52)
        refresh_button.clicked.connect(self.refresh_outputs)
        selector_row.addWidget(refresh_button)
        content_layout.addLayout(selector_row)

        self.library_status = QLabel()
        self.library_status.setObjectName("libraryStatus")
        content_layout.addSpacing(10)
        content_layout.addWidget(self.library_status)

        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.Shape.HLine)
        content_layout.addSpacing(38)
        content_layout.addWidget(divider)
        content_layout.addSpacing(28)

        action_row = QHBoxLayout()
        action_row.setSpacing(12)

        self.run_button = QPushButton("Run")
        self.run_button.setObjectName("runButton")
        self.run_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )
        self.run_button.setIconSize(QSize(18, 18))
        self.run_button.setMinimumHeight(50)
        action_row.addWidget(self.run_button)

        self.view_button = QPushButton("View")
        self.view_button.setObjectName("viewButton")
        self.view_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)
        )
        self.view_button.setIconSize(QSize(18, 18))
        self.view_button.setMinimumHeight(50)
        action_row.addWidget(self.view_button)

        action_row.addStretch()
        content_layout.addLayout(action_row)
        content_layout.addStretch()

        phase_label = QLabel("PHASE 01  /  DESKTOP SHELL")
        phase_label.setObjectName("phaseLabel")
        content_layout.addWidget(phase_label)
        page_layout.addWidget(content, stretch=1)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow#mainWindow, QWidget#centralWidget {
                background: #f3f5f1;
            }
            QWidget#masthead {
                background: #17201d;
            }
            QLabel#editionLabel, QLabel#publicationLabel {
                color: #b9c3bc;
                font-family: "Avenir Next";
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0;
            }
            QLabel#mastheadTitle {
                color: #fffdf7;
                font-family: "Georgia";
                font-size: 44px;
                font-weight: 700;
                letter-spacing: 0;
            }
            QFrame#accentRule {
                background: #e84a3c;
                border: 0;
            }
            QWidget#content {
                background: #f3f5f1;
            }
            QLabel#sectionLabel, QLabel#fieldLabel, QLabel#phaseLabel {
                color: #e04437;
                font-family: "Avenir Next";
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0;
            }
            QLabel#sectionTitle {
                color: #17201d;
                font-family: "Georgia";
                font-size: 30px;
                font-weight: 600;
                letter-spacing: 0;
                margin-top: 8px;
            }
            QLabel#fieldLabel {
                color: #55605b;
                margin-bottom: 8px;
            }
            QComboBox#outputSelector {
                background: #ffffff;
                color: #17201d;
                border: 1px solid #c9ceca;
                border-radius: 4px;
                padding: 0 16px;
                font-family: "Avenir Next";
                font-size: 15px;
                selection-background-color: #dfe8e2;
            }
            QComboBox#outputSelector:hover {
                border-color: #7b8780;
            }
            QComboBox#outputSelector:focus {
                border: 2px solid #28775b;
                padding-left: 15px;
            }
            QComboBox#outputSelector:disabled {
                background: #e7e9e6;
                color: #7b837f;
            }
            QComboBox#outputSelector::drop-down {
                border: 0;
                width: 42px;
            }
            QComboBox#outputSelector QAbstractItemView {
                background: #ffffff;
                color: #17201d;
                border: 1px solid #c9ceca;
                selection-background-color: #dfe8e2;
                selection-color: #17201d;
                padding: 5px;
            }
            QToolButton#refreshButton {
                background: #ffffff;
                border: 1px solid #c9ceca;
                border-radius: 4px;
            }
            QToolButton#refreshButton:hover {
                background: #e7ece8;
                border-color: #7b8780;
            }
            QToolButton#refreshButton:pressed {
                background: #d8dfda;
            }
            QLabel#libraryStatus {
                color: #68716d;
                font-family: "Avenir Next";
                font-size: 12px;
                letter-spacing: 0;
            }
            QFrame#divider {
                color: #cfd4d0;
                background: #cfd4d0;
                border: 0;
                max-height: 1px;
            }
            QPushButton#runButton, QPushButton#viewButton {
                min-width: 126px;
                border-radius: 4px;
                padding: 0 22px;
                font-family: "Avenir Next";
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 0;
            }
            QPushButton#runButton {
                background: #ffffff;
                color: #17201d;
                border: 1px solid #aeb6b1;
            }
            QPushButton#runButton:hover {
                background: #e7ece8;
            }
            QPushButton#viewButton {
                background: #28775b;
                color: #ffffff;
                border: 1px solid #28775b;
            }
            QPushButton#viewButton:hover {
                background: #1f624a;
                border-color: #1f624a;
            }
            QPushButton#viewButton:disabled {
                background: #a9b6b0;
                color: #edf0ee;
                border-color: #a9b6b0;
            }
            QLabel#phaseLabel {
                color: #7b837f;
            }
            """
        )

    def refresh_outputs(self) -> None:
        selected_path = self.selected_output()
        outputs = discover_html_outputs(self.output_dir)

        self.output_selector.clear()
        if not outputs:
            self.output_selector.addItem("No HTML digests found")
            self.output_selector.setEnabled(False)
            self.view_button.setEnabled(False)
            self.library_status.setText(f"0 DIGESTS  /  {self.output_dir}")
            return

        self.output_selector.setEnabled(True)
        self.view_button.setEnabled(True)
        for output in outputs:
            self.output_selector.addItem(output.name, str(output.resolve()))
            self.output_selector.setItemData(
                self.output_selector.count() - 1,
                str(output.resolve()),
                Qt.ItemDataRole.ToolTipRole,
            )

        if selected_path is not None:
            selected_index = self.output_selector.findData(str(selected_path.resolve()))
            if selected_index >= 0:
                self.output_selector.setCurrentIndex(selected_index)

        noun = "DIGEST" if len(outputs) == 1 else "DIGESTS"
        self.library_status.setText(f"{len(outputs)} {noun}  /  {self.output_dir}")

    def selected_output(self) -> Path | None:
        selected_data = self.output_selector.currentData()
        return Path(selected_data) if selected_data else None


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("My News")
    app.setFont(QFont("Avenir Next", 13))

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())