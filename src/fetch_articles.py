from datetime import datetime, timezone
import ssl
from typing import Any

import feedparser
import httpx
import trafilatura
import truststore

from src.models.article_content import ArticleContent

"""
Ok so one problem we're running into is the variance in how some places store their RSS, the summary can sometimes be a summary 
and sometimes it can be the full article or not exist at all, so we need to account for this too.
The way we do this is by checking if summary exists, if it does we will use it whether or not its the full article or
just an actual summary, doesn't really matter. But if it doesn't exist we will try and extract the full article body and
normalise that, then upload it to the database.
"""

def _fetch_body_from_url(url: str, client: httpx.Client) -> str:
    """Fallback: fetch and extract article body directly from the article page."""
    try:
        response = client.get(url)
        response.raise_for_status()
    except httpx.HTTPError:
        return ""
    extracted = trafilatura.extract(response.text)
    return extracted or ""


def _get_published_at(entry: feedparser.FeedParserDict) -> datetime | None:
    published = entry.get("published_parsed") or entry.get("updated_parsed")
    if published is None:
        return None
    return datetime(*published[:6], tzinfo=timezone.utc)


class FetchArticlesError(RuntimeError):
    """Raised when no configured source can provide articles."""


def fetch_articles(
    sources: list[dict[str, Any]],
    max_articles_per_source: int = 20,
    user_agent: str | None = None,
    connect_timeout_seconds: float = 10,
    read_timeout_seconds: float = 20,
) -> dict[str, ArticleContent]:
    """Fetch linked articles from each enabled RSS source."""
    articles: dict[str, ArticleContent] = {}
    failures: list[str] = []
    ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    headers = {"User-Agent": user_agent} if user_agent else None
    timeout = httpx.Timeout(
        connect=connect_timeout_seconds,
        read=read_timeout_seconds,
        write=read_timeout_seconds,
        pool=connect_timeout_seconds,
    )

    with httpx.Client(
        verify=ssl_context,
        follow_redirects=True,
        timeout=timeout,
        headers=headers,
    ) as client:
        for source in sources:
            if not source.get("enabled", True):
                continue

            source_id = source["id"]
            try:
                response = client.get(source["url"])
                response.raise_for_status()
            except httpx.HTTPError as exc:
                failures.append(f"{source_id}: {exc}")
                continue

            feed = feedparser.parse(response.content)
            if not feed.entries:
                failures.append(f"{source_id}: feed contained no entries")
                continue

            for entry in feed.entries[:max_articles_per_source]:
                article_url = entry.get("link")
                if not article_url or article_url in articles:
                    continue

                title = entry.get("title", "Untitled").strip()
                body = entry.get("summary", "").strip()
                if not body:
                    body = _fetch_body_from_url(article_url, client)
                articles[article_url] = ArticleContent(
                    title=title,
                    body=body,
                    source_id=source_id,
                    published_at=_get_published_at(entry),
                )

    if not articles and failures:
        raise FetchArticlesError("No sources returned articles: " + "; ".join(failures))

    return articles

