import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from src.gui import MainWindow, discover_html_outputs


@pytest.fixture(scope="module")
def qt_app() -> QApplication:
    app = QApplication.instance() or QApplication([])
    yield app


def test_discover_html_outputs_returns_newest_html_first(tmp_path: Path) -> None:
    older = tmp_path / "older.html"
    newer = tmp_path / "newer.HTML"
    ignored = tmp_path / "digest.pdf"

    older.write_text("older")
    newer.write_text("newer")
    ignored.write_text("not html")
    os.utime(older, (1, 1))
    os.utime(newer, (2, 2))

    assert discover_html_outputs(tmp_path) == [newer, older]


def test_main_window_populates_output_selector(qt_app: QApplication, tmp_path: Path) -> None:
    output = tmp_path / "digest.html"
    output.write_text("<html></html>")

    window = MainWindow(tmp_path)

    assert window.output_selector.count() == 1
    assert window.output_selector.currentText() == "digest.html"
    assert window.selected_output() == output.resolve()
    assert window.view_button.isEnabled()

    window.close()


def test_main_window_disables_view_for_empty_library(
    qt_app: QApplication,
    tmp_path: Path,
) -> None:
    window = MainWindow(tmp_path)

    assert window.output_selector.currentText() == "No HTML digests found"
    assert not window.output_selector.isEnabled()
    assert not window.view_button.isEnabled()

    window.close()