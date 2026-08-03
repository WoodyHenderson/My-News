from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from PyQt6.QtCore import QObject, QSize, Qt, QThread, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QFont
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
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"


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


class RunDigestWorker(QObject):
    progress = pyqtSignal(str, str)
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, config_path: Path, output_path: Path) -> None:
        super().__init__()
        self.config_path = config_path
        self.output_path = output_path

    def run(self) -> None:
        try:
            from src.commands.config_run import run_application

            run_application(
                config_path=self.config_path,
                output_path=self.output_path,
                on_progress=self.progress.emit,
            )
            self.finished.emit(str(self.output_path.resolve()))
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(
        self,
        output_dir: Path = DEFAULT_OUTPUT_DIR,
        config_path: Path = DEFAULT_CONFIG_PATH,
    ) -> None:
        super().__init__()
        self.output_dir = output_dir
        self.config_path = config_path
        self._run_thread: QThread | None = None
        self._run_worker: RunDigestWorker | None = None

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
        self.run_button.clicked.connect(self.run_digest)
        action_row.addWidget(self.run_button)

        self.view_button = QPushButton("View")
        self.view_button.setObjectName("viewButton")
        self.view_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)
        )
        self.view_button.setIconSize(QSize(18, 18))
        self.view_button.setMinimumHeight(50)
        self.view_button.clicked.connect(self.view_selected_output)
        action_row.addWidget(self.view_button)

        action_row.addStretch()
        content_layout.addLayout(action_row)
        content_layout.addStretch()

        self.run_status = QLabel("Ready.")
        self.run_status.setObjectName("runStatus")
        content_layout.addSpacing(14)
        content_layout.addWidget(self.run_status)

        phase_label = QLabel("PHASE 03  /  LINKED COMMANDS")
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
            QLabel#runStatus {
                color: #33403a;
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

    def run_digest(self) -> None:
        if self._run_thread is not None:
            return

        output_path = self.output_dir / f"my-news-{date.today().isoformat()}.html"
        self._set_running_state(True)
        self.run_status.setText("Starting digest run...")

        self._run_worker = RunDigestWorker(self.config_path, output_path)
        self._run_thread = QThread(self)
        self._run_worker.moveToThread(self._run_thread)

        self._run_thread.started.connect(self._run_worker.run)
        self._run_worker.progress.connect(self._on_run_progress)
        self._run_worker.finished.connect(self._on_run_finished)
        self._run_worker.failed.connect(self._on_run_failed)
        self._run_worker.finished.connect(self._run_thread.quit)
        self._run_worker.failed.connect(self._run_thread.quit)
        self._run_thread.finished.connect(self._cleanup_run_thread)

        self._run_thread.start()

    def view_selected_output(self) -> None:
        selected = self.selected_output()
        if selected is None:
            self.run_status.setText("No digest selected to open.")
            return

        if not selected.exists():
            self.run_status.setText("Selected digest no longer exists. Refreshing list...")
            self.refresh_outputs()
            return

        opened = QDesktopServices.openUrl(QUrl.fromLocalFile(str(selected.resolve())))
        if opened:
            self.run_status.setText(f"Opened {selected.name}")
        else:
            self.run_status.setText("Could not open the selected digest.")

    def _on_run_progress(self, message: str, level: str) -> None:
        if level == "error":
            self.run_status.setText(f"Error: {message}")
            return
        self.run_status.setText(message)

    def _on_run_finished(self, output_path: str) -> None:
        self._set_running_state(False)
        self.refresh_outputs()
        self.run_status.setText(f"Digest complete: {output_path}")

    def _on_run_failed(self, error_message: str) -> None:
        self._set_running_state(False)
        self.run_status.setText(f"Digest failed: {error_message}")

    def _cleanup_run_thread(self) -> None:
        self._run_thread = None
        self._run_worker = None

    def _set_running_state(self, running: bool) -> None:
        has_selected_output = self.selected_output() is not None
        self.run_button.setEnabled(not running)
        self.output_selector.setEnabled(not running and has_selected_output)
        self.view_button.setEnabled(not running and has_selected_output)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("My News")
    app.setFont(QFont("Avenir Next", 13))

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())