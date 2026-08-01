from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from weasyprint import HTML

from src.models.ranked_article import RankedArticle

_PDF_DIRECTORY = Path(__file__).resolve().parent


def generate_pdf(
    ranked_articles: Sequence[tuple[str, RankedArticle]],
    output_path: Path | None = None,
    *,
    digest_config: Mapping[str, object] | None = None,
) -> Path:
    """Render a simple PDF digest ordered from highest to lowest score."""
    config = digest_config or {}
    generated_at = datetime.now(UTC)
    articles = sorted(ranked_articles, key=lambda item: item[1].score, reverse=True)

    if output_path is None:
        output_directory = Path(str(config.get("output_directory", "output")))
        filename = str(config.get("filename", "digest-{date}.pdf"))
        output_path = output_directory / filename.replace(
            "{date}", generated_at.date().isoformat()
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

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

    HTML(string=rendered_html, base_url=_PDF_DIRECTORY.as_uri()).write_pdf(output_path)

    return output_path
