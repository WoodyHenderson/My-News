from __future__ import annotations

from pathlib import Path

from src.commands.config_validation import ConfigValidationError, load_and_validate_config
from fetch_articles import fetch_articles, ArticleContent
from normalise import normalise_validate_articles

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
) -> None:
    """
    Run the application with the specified configuration file and output path.
    """
    try:
        config_data = load_and_validate_config(config_path)
    except ConfigValidationError as e:
        raise ConfigRunError(f"Configuration validation failed: {e}") from e

    # Lets start by gathering all the sources from the configuration file
    urls = config_data.get("url", []) 
    article_data = fetch_articles(urls)
    article_data = normalise_validate_articles(article_data)
    

    