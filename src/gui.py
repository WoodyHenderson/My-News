from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import yaml
from PyQt6.QtCore import QObject, QSize, Qt, QThread, QUrl, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStyle,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QScrollArea,
)

from src.html_viewer import HtmlViewerWindow
from src.output_generation.generate_digest import _write_pdf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"
CATALOG_DIR = PROJECT_ROOT / "config_catalog"

PROVIDER_BRANDS = {
    "associated_press": ("AP", "#f04e30", "#ffffff"),
    "bbc": ("BBC", "#bb1919", "#ffffff"),
    "cnbc": ("CNBC", "#005594", "#ffffff"),
    "guardian": ("G", "#052962", "#ffffff"),
    "propublica": ("PP", "#111111", "#ffffff"),
    "reuters": ("R", "#ff8000", "#17201d"),
}


class ManageDigestDialog(QDialog):
    """Dialog to select categories and providers for digest generation."""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("manageDigestDialog")
        self.setWindowTitle("Manage Digest")
        self.setMinimumSize(560, 480)

        self._category_checks: dict[str, QCheckBox] = {}
        self._provider_checks: dict[str, QCheckBox] = {}

        self._build_ui()
        self._apply_styles()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Tab widget for categories and providers
        tabs = QTabWidget()
        tabs.addTab(self._build_categories_tab(), "Categories")
        tabs.addTab(self._build_providers_tab(), "Providers")
        layout.addWidget(tabs)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.accept)
        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def _build_categories_tab(self) -> QWidget:
        """Build the categories selection tab."""
        container = QWidget()
        layout = QVBoxLayout(container)

        categories_dir = CATALOG_DIR / "categories"
        if not categories_dir.exists():
            layout.addWidget(QLabel("No categories found."))
            return container

        category_files = sorted([f.stem for f in categories_dir.glob("*.yaml")])

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        for category in category_files:
            checkbox = QCheckBox(category.replace("_", " ").title())
            checkbox.setObjectName(category)
            checkbox.setChecked(True)
            self._category_checks[category] = checkbox
            scroll_layout.addWidget(checkbox)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        return container

    def _build_providers_tab(self) -> QWidget:
        """Build the providers selection tab."""
        container = QWidget()
        container.setObjectName("providersTab")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(18, 18, 18, 18)

        publishers_dir = CATALOG_DIR / "publishers"
        if not publishers_dir.exists():
            layout.addWidget(QLabel("No providers found."))
            return container

        provider_files = sorted([f.stem for f in publishers_dir.glob("*.yaml")])

        scroll_area = QScrollArea()
        scroll_area.setObjectName("providersScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setObjectName("providersScrollContent")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)

        for provider in provider_files:
            provider_file = publishers_dir / f"{provider}.yaml"
            display_name = provider.replace("_", " ").title()
            description = ""
            try:
                provider_data = yaml.safe_load(provider_file.read_text(encoding="utf-8"))
                if provider_data and isinstance(provider_data[0], dict):
                    display_name = provider_data[0].get("name", display_name)
                    description = provider_data[0].get("description", "")
            except (OSError, yaml.YAMLError):
                pass

            row = QFrame()
            row.setObjectName("providerRow")
            row.setMinimumHeight(64)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(18, 10, 14, 10)
            row_layout.setSpacing(16)

            name_label = QLabel(display_name)
            name_label.setObjectName("providerName")
            if description:
                name_label.setToolTip(description)
            row_layout.addWidget(name_label)
            row_layout.addStretch()

            monogram, background, foreground = PROVIDER_BRANDS.get(
                provider,
                (display_name[:2].upper(), "#55605b", "#ffffff"),
            )
            icon_label = QLabel(monogram)
            icon_label.setObjectName("providerIcon")
            icon_label.setAccessibleName(f"{display_name} icon")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setFixedSize(54, 32)
            icon_label.setStyleSheet(
                f"background: {background}; color: {foreground};"
            )
            row_layout.addWidget(icon_label)

            checkbox = QCheckBox()
            checkbox.setObjectName(provider)
            checkbox.setAccessibleName(f"Include {display_name}")
            checkbox.setToolTip(f"Include {display_name} in the digest")
            checkbox.setChecked(True)
            self._provider_checks[provider] = checkbox
            row_layout.addWidget(checkbox)
            scroll_layout.addWidget(row)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        return container

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QDialog#manageDigestDialog {
                background: #f3f5f1;
            }
            QDialog#manageDigestDialog QTabWidget::pane {
                background: #f7f8f5;
                border: 1px solid #c9ceca;
                border-radius: 4px;
                top: -1px;
            }
            QDialog#manageDigestDialog QTabBar::tab {
                background: #e5e9e5;
                color: #4d5852;
                border: 1px solid #c9ceca;
                padding: 10px 24px;
                font-family: "Avenir Next";
                font-size: 13px;
                font-weight: 600;
            }
            QDialog#manageDigestDialog QTabBar::tab:selected {
                background: #f7f8f5;
                color: #17201d;
                border-bottom-color: #f7f8f5;
            }
            QWidget#providersTab, QWidget#providersScrollContent,
            QScrollArea#providersScrollArea {
                background: #f7f8f5;
                border: 0;
            }
            QFrame#providerRow {
                background: #ffffff;
                border: 1px solid #d2d7d3;
                border-radius: 4px;
            }
            QLabel#providerName {
                color: #17201d;
                font-family: "Avenir Next";
                font-size: 15px;
                font-weight: 600;
            }
            QLabel#providerIcon {
                border: 0;
                border-radius: 3px;
                font-family: "Avenir Next";
                font-size: 11px;
                font-weight: 800;
            }
            QFrame#providerRow QCheckBox::indicator {
                width: 22px;
                height: 22px;
            }
            QDialog#manageDigestDialog QPushButton {
                min-width: 92px;
                min-height: 38px;
                border: 1px solid #aeb6b1;
                border-radius: 4px;
                background: #ffffff;
                color: #17201d;
                font-family: "Avenir Next";
                font-size: 13px;
                font-weight: 600;
            }
            QDialog#manageDigestDialog QPushButton:hover {
                background: #e7ece8;
            }
            """
        )

    def get_selected_categories(self) -> list[str]:
        """Return list of selected category keys."""
        return [
            key
            for key, checkbox in self._category_checks.items()
            if checkbox.isChecked()
        ]

    def get_selected_providers(self) -> list[str]:
        """Return list of selected provider keys."""
        return [
            key
            for key, checkbox in self._provider_checks.items()
            if checkbox.isChecked()
        ]


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

    def __init__(
        self,
        config_path: Path,
        output_path: Path,
        max_articles_override: int | None,
        provider_pref: list[str] | None = None,
        category_pref: list[str] | None = None,
    ) -> None:
        super().__init__()
        self.config_path = config_path
        self.output_path = output_path
        self.max_articles_override = max_articles_override
        self.provider_pref = provider_pref
        self.category_pref = category_pref

    def run(self) -> None:
        try:
            from src.commands.config_run import run_application

            run_application(
                config_path=self.config_path,
                output_path=self.output_path,
                on_progress=self.progress.emit,
                max_articles_override=self.max_articles_override,
                provider_pref=self.provider_pref,
                category_pref=self.category_pref,
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
        self._viewer_window: HtmlViewerWindow | None = None
        self._manage_digest_dialog: ManageDigestDialog | None = None
        
        # Initialize with all available categories and providers selected by default
        categories_dir = CATALOG_DIR / "categories"
        self._selected_categories = sorted([f.stem for f in categories_dir.glob("*.yaml")]) if categories_dir.exists() else []
        publishers_dir = CATALOG_DIR / "publishers"
        self._selected_providers = sorted([f.stem for f in publishers_dir.glob("*.yaml")]) if publishers_dir.exists() else []

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

        max_articles_label = QLabel("MAX ARTICLES")
        max_articles_label.setObjectName("fieldLabel")
        content_layout.addSpacing(18)
        content_layout.addWidget(max_articles_label)

        self.max_articles_selector = QComboBox()
        self.max_articles_selector.setObjectName("maxArticlesSelector")
        self.max_articles_selector.setMinimumHeight(44)
        self.max_articles_selector.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )
        self.max_articles_selector.addItem("ALL", 0)
        for value in (10, 20, 30, 40, 50):
            self.max_articles_selector.addItem(str(value), value)
        self.max_articles_selector.setCurrentIndex(
            self.max_articles_selector.findData(30)
        )
        content_layout.addWidget(self.max_articles_selector)

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

        self.manage_button = QPushButton("Manage Digest")
        self.manage_button.setObjectName("manageButton")
        self.manage_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogListView)
        )
        self.manage_button.setIconSize(QSize(18, 18))
        self.manage_button.setMinimumHeight(50)
        self.manage_button.clicked.connect(self._open_manage_digest_dialog)
        action_row.addWidget(self.manage_button)

        self.view_button = QPushButton("View")
        self.view_button.setObjectName("viewButton")
        self.view_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)
        )
        self.view_button.setIconSize(QSize(18, 18))
        self.view_button.setMinimumHeight(50)
        self.view_button.clicked.connect(self.view_selected_output)
        action_row.addWidget(self.view_button)

        self.as_pdf_button = QPushButton("Export PDF")
        self.as_pdf_button.setObjectName("asPdfButton")
        self.as_pdf_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
        )
        self.as_pdf_button.setIconSize(QSize(18, 18))
        self.as_pdf_button.setMinimumHeight(50)
        self.as_pdf_button.clicked.connect(self.export_selected_output_as_pdf)
        action_row.addWidget(self.as_pdf_button)

        action_row.addStretch()
        content_layout.addLayout(action_row)
        content_layout.addStretch()

        self.run_status = QLabel("Ready.")
        self.run_status.setObjectName("runStatus")
        content_layout.addSpacing(14)
        content_layout.addWidget(self.run_status)

        phase_label = QLabel("PRAYERS IT WORKS")
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
            QComboBox#maxArticlesSelector {
                background: #ffffff;
                color: #17201d;
                border: 1px solid #c9ceca;
                border-radius: 4px;
                padding: 0 12px;
                min-width: 110px;
                font-family: "Avenir Next";
                font-size: 14px;
            }
            QComboBox#maxArticlesSelector:hover {
                border-color: #7b8780;
            }
            QComboBox#maxArticlesSelector:focus {
                border: 2px solid #28775b;
                padding-left: 11px;
            }
            QComboBox#maxArticlesSelector:disabled {
                background: #e7e9e6;
                color: #7b837f;
            }
            QComboBox#maxArticlesSelector::drop-down {
                border: 0;
                width: 34px;
            }
            QComboBox#maxArticlesSelector QAbstractItemView {
                background: #ffffff;
                color: #17201d;
                border: 1px solid #c9ceca;
                selection-background-color: #dfe8e2;
                selection-color: #17201d;
                padding: 4px;
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
            QPushButton#runButton, QPushButton#manageButton {
                background: #ffffff;
                color: #17201d;
                border: 1px solid #aeb6b1;
            }
            QPushButton#runButton:hover, QPushButton#manageButton:hover {
                background: #e7ece8;
            }
            QPushButton#manageButton {
                min-width: 160px;
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
        most_recent = outputs[0] if outputs else None

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
            selected_index = self.output_selector.findData(str(most_recent.resolve()))
            if selected_index >= 0:
                self.output_selector.setCurrentIndex(selected_index)

        noun = "DIGEST" if len(outputs) == 1 else "DIGESTS"
        self.library_status.setText(f"{len(outputs)} {noun}  /  {self.output_dir}")

    def selected_output(self) -> Path | None:
        selected_data = self.output_selector.currentData()
        return Path(selected_data) if selected_data else None

    def _open_manage_digest_dialog(self) -> None:
        """Open the Manage Digest dialog to select categories and providers."""
        self._manage_digest_dialog = ManageDigestDialog(self)
        if self._manage_digest_dialog.exec() == QDialog.DialogCode.Accepted:
            self._selected_categories = self._manage_digest_dialog.get_selected_categories()
            self._selected_providers = self._manage_digest_dialog.get_selected_providers()
            categories_str = ", ".join(self._selected_categories) or "None"
            providers_str = ", ".join(self._selected_providers) or "None"
            self.run_status.setText(
                f"Categories: {categories_str} | Providers: {providers_str}"
            )

    def run_digest(self) -> None:
        if self._run_thread is not None:
            return

        output_path = self.output_dir / f"my-news-{date.today().isoformat()}.html"
        selected_max_articles = int(self.max_articles_selector.currentData())
        self._set_running_state(True)
        self.run_status.setText("Starting digest run...")

        self._run_worker = RunDigestWorker(
            self.config_path,
            output_path,
            selected_max_articles,
            provider_pref=self._selected_providers,
            category_pref=self._selected_categories,
        )
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

    def export_selected_output_as_pdf(self) -> None:
        selected = self.selected_output()
        if selected is None:
            self.run_status.setText("No digest selected to export.")
            return

        if not selected.exists():
            self.run_status.setText("Selected digest no longer exists. Refreshing list...")
            self.refresh_outputs()
            return

        pdf_output_path = selected.with_suffix(".pdf")
        try:
            _write_pdf(selected.read_text(encoding="utf-8"), pdf_output_path)
            self.run_status.setText(f"Exported PDF: {pdf_output_path.name}")
        except Exception as exc:
            self.run_status.setText(f"Failed to export PDF: {exc}")

    def view_selected_output(self) -> None:
        selected = self.selected_output()
        if selected is None:
            self.run_status.setText("No digest selected to open.")
            return

        if not selected.exists():
            self.run_status.setText("Selected digest no longer exists. Refreshing list...")
            self.refresh_outputs()
            return

        try:
            self._viewer_window = HtmlViewerWindow(selected)
        except RuntimeError as exc:
            self.run_status.setText("Viewer failed to initialize")
            QMessageBox.critical(self, "Viewer Error", str(exc))
            return

        self._viewer_window.show()
        self._viewer_window.raise_()
        self._viewer_window.activateWindow()
        self.run_status.setText(f"Viewing {selected.name} in app")

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
        self.max_articles_selector.setEnabled(not running)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("My News")
    app.setFont(QFont("Avenir Next", 13))

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())