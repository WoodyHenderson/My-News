from __future__ import annotations

from pathlib import Path
from typing import Callable

from src.commands.config_validation import ConfigValidationError, load_and_validate_config
from src.fetch_articles import fetch_articles
from src.models.article_content import ArticleContent
from src.normalise import normalise_validate_articles
from src.ranking import rank_articles
from src.output_generation.generate_digest import generate_digest
from src.compare_to_db import compare_to_seen

'''
What run should include:

1. Load and validate the configuration file.
2a. If configuration is invalid, raise ConfigRunError with a descriptive message.
2b. If configuration is valid, proceed.
3. We need to first gather all the sources from the configuration file.
4. For each source, we need to fetch the articles.
4a. Normalise and validate fields of articles (e.g., clean up text, remove duplicates).
4b. Persist the normalised articles to SQLite database.
4c. Weigh and Rank the articles based on the configuration file
4d. Persist ranking outputs and score breakdown
5. Generate the final output based on the ranked articles and the configuration file.
'''


class ConfigRunError(ValueError):
    """Raised when the application cannot run due to configuration issues."""


'''
EXAMPLE 
sources:
  # BBC publishes separate RSS feeds for each requested section.
  - id: "bbc-front-page"
    name: "BBC News - Front Page"
    enabled: true
    kind: "feed"
    url: "https://feeds.bbci.co.uk/news/rss.xml"
    site_url: "https://www.bbc.co.uk/news"
    priority_boost: 0.5
    interests:
      - "general-news"
      - "gaming"
      - "ai"
    fetch_article: "auto"
'''

def run_application(
    config_path: Path,
    output_path: Path | None = None,
    on_progress: Callable[[str, str], None] | None = None,
) -> None:
    """
    Run the application with the specified configuration file and output path.

    on_progress is an optional callback called with (message, level) where level
    is one of 'info', 'success', or 'error'.
    """
    def progress(msg: str, level: str = "info") -> None:
        if on_progress:
            on_progress(msg, level)

    try:
        progress("Loading and validating configuration...")
        config_data = load_and_validate_config(config_path)
        progress("Configuration validated successfully", "success")
    except ConfigValidationError as e:
        progress(f"Configuration validation failed: {e}", "error")
        raise ConfigRunError(f"Configuration validation failed: {e}") from e

    # Lets start by gathering all the sources from the configuration file
    try:
        progress("Gathering sources from configuration...")
        sources = config_data.get("sources", [])
    except Exception as e:
        progress(f"Failed to gather sources from configuration: {e}", "error")
        raise ConfigRunError(f"Failed to gather sources from configuration: {e}") from e
    try:
        progress(f"Fetching articles from {len(sources)} sources...")
        max_articles_per_source = config_data.get("network", {}).get(
            "max_article_fetches_per_source", 20
        )
        article_data = fetch_articles(sources, max_articles_per_source)
        progress(f"Successfully fetched {len(article_data)} articles", "success")
    except Exception as e:
        progress(f"Failed to fetch articles: {e}", "error")
        raise ConfigRunError(f"Failed to fetch articles: {e}") from e
    try:
        progress(f"Normalising and validating {len(article_data)} articles...")
        article_data = normalise_validate_articles(article_data)
        progress(f"Successfully normalised {len(article_data)} articles", "success")
    except Exception as e:
        progress(f"Failed to normalise and validate articles: {e}", "error")
        raise ConfigRunError(f"Failed to normalise and validate articles: {e}") from e
    try:
        progress(f"Comparing against previously seen articles...")
        ranked_articles = compare_to_seen(ranked_articles)
        progress(f"Successfully compared against previously seen articles", "success")
    except Exception as e:
        progress(f"Failed to compare against previously seen articles: {e}", "error")
        raise ConfigRunError(f"Failed to compare against previously seen articles: {e}") from e
    try:
        progress(f"Scoring and ranking {len(article_data)} articles based on your preferences...")
        ranked_articles = rank_articles(article_data, config_path)
        progress(
            f"Successfully scored {len(article_data)} articles and selected "
            f"{len(ranked_articles)} for the digest",
            "success",
        )
    except Exception as e:
        progress(f"Failed to rank articles: {e}", "error")
        raise ConfigRunError(f"Failed to rank articles: {e}") from e
    try:
        progress("Generating digest output...")
        digest_path = generate_digest(
            ranked_articles,
            output_path,
            digest_config=config_data.get("digest", {}),
        )
        progress(f"Successfully generated digest at {digest_path}", "success")
    except Exception as e:
        progress(f"Failed to generate digest output: {e}", "error")
        raise ConfigRunError(f"Failed to generate digest output: {e}") from e

    