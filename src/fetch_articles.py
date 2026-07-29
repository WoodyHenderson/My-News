from dataclasses import dataclass
import feedparser
import trafilatura

@dataclass
class ArticleContent:
    header: str
    body: str

def _fetch_body_from_url(url: str) -> str:
    """Fallback: fetch and extract article body directly from the article page."""
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        return ""
    extracted = trafilatura.extract(downloaded)
    return extracted or ""

def fetch_articles(urls: list[str]) -> dict[str, ArticleContent]:
    """Here we go to each URL and fetch the RSS and give it back to the user as a dictionary with key url and value as ArticleContent"""
    articles = {}
    for url in urls:
        feed = feedparser.parse(url)
        if feed.entries:
            entry = feed.entries[0]
            header = entry.get("title", "")
            body = entry.get("summary", "")
            if not body and entry.get("link"):
                body = _fetch_body_from_url(entry.link)
            articles[url] = ArticleContent(header=header, body=body)
        else:
            articles[url] = ArticleContent(header="No entries found", body="")
    return articles

