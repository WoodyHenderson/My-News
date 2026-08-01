from datetime import datetime, timezone
import feedparser
import trafilatura

from src.models.article_content import ArticleContent

"""
Ok so one problem we're running into is the variance in how some places store their RSS, the summary can sometimes be a summary 
and sometimes it can be the full article or not exist at all, so we need to account for this too.
The way we do this is by checking if summary exists, if it does we will use it whether or not its the full article or
just an actual summary, doesn't really matter. But if it doesn't exist we will try and extract the full article body and
normalise that, then upload it to the database.
"""

def _fetch_body_from_url(url: str) -> str:
    """Fallback: fetch and extract article body directly from the article page."""
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        return ""
    extracted = trafilatura.extract(downloaded)
    return extracted or ""


def _get_published_at(entry: feedparser.FeedParserDict) -> datetime | None:
    published = entry.get("published_parsed") or entry.get("updated_parsed")
    if published is None:
        return None
    return datetime(*published[:6], tzinfo=timezone.utc)


def fetch_articles(urls: list[str]) -> dict[str, ArticleContent]:
    """Here we go to each URL and fetch the RSS and give it back to the user as a dictionary with key url and value as ArticleContent"""
    articles = {}
    for url in urls:
        feed = feedparser.parse(url)
        if feed.entries:
            entry = feed.entries[0]
            title = entry.title.strip()
            # if summary exists, use it as the body otherwise try and fetch the body from the article page
            body = entry.get("summary", "").strip()
            if not body and entry.get("link"):
                body = _fetch_body_from_url(entry.link)
            articles[url] = ArticleContent(
                title=title,
                body=body,
                source_id=url,
                published_at=_get_published_at(entry),
            )
        else:
            articles[url] = ArticleContent(
                title="No entries found",
                body="",
                source_id=url,
                published_at=None,
            )
    return articles

