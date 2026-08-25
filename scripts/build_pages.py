from pathlib import Path
from shutil import rmtree

from src.commands.config_validation import CatalogSelection
from src.commands.config_run import run_application

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PAGES_DIST_DIR = PROJECT_ROOT / "pages-dist"

def main() -> None:
    if PAGES_DIST_DIR.exists():
        rmtree(PAGES_DIST_DIR)

    PAGES_DIST_DIR.mkdir(parents=True, exist_ok=True)

    run_application(
        config_path=PROJECT_ROOT / "config" / "default.yaml",
        output_path=PAGES_DIST_DIR / "index.html",
        catalog_selection=CatalogSelection.ALL,
    )

if __name__ == "__main__":
    main()