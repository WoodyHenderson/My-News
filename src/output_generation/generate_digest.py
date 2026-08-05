from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from shutil import copy2
from warnings import warn

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from src.models.ranked_article import RankedArticle

_PDF_DIRECTORY = Path(__file__).resolve().parent
_HTML_SUFFIXES = {".htm", ".html"}
_ASSET_FILES = {"styles.css", "digest.js"}


def _copy_html_assets(output_path: Path) -> None:
    target_dir = output_path.parent
    for asset_name in _ASSET_FILES:
        source = _PDF_DIRECTORY / asset_name
        target = target_dir / asset_name
        if source.exists():
            copy2(source, target)
        else:
            warn(f"Missing HTML asset: {source}", stacklevel=2)

def _render_digest_html(
    ranked_articles: Sequence[tuple[str, RankedArticle]],
    *,
    digest_config: Mapping[str, object] | None = None,
) -> tuple[str, Path]:
    config = digest_config or {}
    generated_at = datetime.now(UTC)
    articles = sorted(ranked_articles, key=lambda item: item[1].score, reverse=True)

    environment = Environment(
        loader=FileSystemLoader(_PDF_DIRECTORY),
        autoescape=select_autoescape(("html", "xml")),
        undefined=StrictUndefined,
    )
    rendered_html = environment.get_template("digest.html").render(
        title=str(config.get("title", "My News")),
        generated_at=generated_at,
        articles=articles,
        show_match_reasons=bool(config.get("show_match_reasons", True)),
    )

    return rendered_html, _PDF_DIRECTORY


def _write_html(rendered_html: str, output_path: Path) -> None:
    output_path.write_text(rendered_html, encoding="utf-8")


def _write_pdf(rendered_html: str, output_path: Path) -> None:
    from weasyprint import HTML

    HTML(string=rendered_html, base_url=_PDF_DIRECTORY.as_uri()).write_pdf(output_path)


def generate_digest(
    ranked_articles: Sequence[tuple[str, RankedArticle]],
    output_path: Path | None = None,
    *,
    digest_config: Mapping[str, object] | None = None,
) -> Path:
    """Render a simple digest ordered from highest to lowest score."""
    config = digest_config or {}

    if output_path is None:
        output_directory = Path(str(config.get("output_directory", "output")))
        filename = str(config.get("filename", "digest-{date}.pdf"))
        output_path = output_directory / filename.replace(
            "{date}", datetime.now(UTC).date().isoformat()
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    rendered_html, _ = _render_digest_html(ranked_articles, digest_config=config)

    if output_path.suffix.lower() in _HTML_SUFFIXES:
        _write_html(rendered_html, output_path)
        _copy_html_assets(output_path)
        return output_path

    try:
        _write_pdf(rendered_html, output_path)
        return output_path
    except Exception as exc:
        fallback_path = output_path.with_suffix(".html")
        _write_html(rendered_html, fallback_path)
        _copy_html_assets(fallback_path)
        warn(
            f"WeasyPrint is unavailable or failed to render the PDF ({exc!s}). "
            f"Wrote HTML output to {fallback_path} instead.",
            stacklevel=2,
        )
        return fallback_path
