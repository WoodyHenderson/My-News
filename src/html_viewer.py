from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QWidget

try:
    # Import WebEngine before QApplication is created to satisfy Qt initialization rules.
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except Exception as exc:  # pragma: no cover - platform/environment specific
    QWebEngineView = None
    _WEBENGINE_IMPORT_ERROR = exc
else:
    _WEBENGINE_IMPORT_ERROR = None


class HtmlViewerWindow(QMainWindow):
    """Simple Chromium-backed window for viewing generated digest HTML."""

    def __init__(self, html_path: Path) -> None:
        super().__init__()
        self.html_path = html_path.resolve()

        self.setWindowTitle(f"My News Viewer - {self.html_path.name}")
        self.setMinimumSize(900, 650)
        self.resize(1200, 760)

        self.web_view = self._create_web_view()
        self.setCentralWidget(self.web_view)
        self._load_html()

    def _create_web_view(self) -> QWidget:
        if QWebEngineView is None:
            raise RuntimeError(
                "Could not initialize Qt WebEngine. Install PyQt6-WebEngine and "
                "ensure WebEngine is imported before QApplication is created."
            ) from _WEBENGINE_IMPORT_ERROR

        return QWebEngineView(self)

    def _load_html(self) -> None:
        if not self.html_path.exists():
            QMessageBox.warning(
                self,
                "Digest Missing",
                f"Could not find the selected digest:\n{self.html_path}",
            )
            return

        self.web_view.load(QUrl.fromLocalFile(str(self.html_path)))
