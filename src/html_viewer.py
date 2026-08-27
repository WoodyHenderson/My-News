from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QUrl, QObject, pyqtSlot
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QWidget
from PyQt6.QtWebChannel import QWebChannel

from src.seen_articles import mark_seen

try:
    # Import WebEngine before QApplication is created to satisfy Qt initialization rules.
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEnginePage
except Exception as exc:  # pragma: no cover - platform/environment specific
    QWebEngineView = None
    QWebEnginePage = None
    _WEBENGINE_IMPORT_ERROR = exc
else:
    _WEBENGINE_IMPORT_ERROR = None


class ExternalLinkPage(QWebEnginePage):
    """Keep digest loaded in-app; open clicked web links in the default browser."""

    def acceptNavigationRequest(self, url: QUrl, nav_type: int, is_main_frame: bool) -> bool:
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked and url.scheme() in {"http", "https"}:
            QDesktopServices.openUrl(url)
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


class SeenBridge(QObject):
    @pyqtSlot(str, result=bool)
    def markSeen(self, url: str) -> bool:
        mark_seen(url)
        return True

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

        self.channel = QWebChannel(self.web_view.page())
        self.bridge = SeenBridge()
        self.channel.registerObject("pyBridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        self._load_html()

    def _create_web_view(self) -> QWidget:
        if QWebEngineView is None or QWebEnginePage is None:
            raise RuntimeError(
                "Could not initialize Qt WebEngine. Install PyQt6-WebEngine and "
                "ensure WebEngine is imported before QApplication is created."
            ) from _WEBENGINE_IMPORT_ERROR

        view = QWebEngineView(self)
        view.setPage(ExternalLinkPage(view))
        return view

    def _load_html(self) -> None:
        if not self.html_path.exists():
            QMessageBox.warning(
                self,
                "Digest Missing",
                f"Could not find the selected digest:\n{self.html_path}",
            )
            return

        self.web_view.load(QUrl.fromLocalFile(str(self.html_path)))

class PyBridge(QObject):
    """Bridge for JavaScript to call Python functions."""

    @pyqtSlot(str)
    def markSeen(self, url: str) -> bool:
        """Mark the given URL as seen"""
        try:
            mark_seen(url)
            return True
        except Exception as exc:
            return False