from dataclasses import dataclass
import feedparser

@dataclass
class ArticleContent:
    header: str
    body: str

def fetch_articles(urls: list[str]) -> dict[str, ArticleContent]:
    """Here we go to each URL and fetch the RSS and give it back to the user as a dictionary with key url and value as ArticleContent"""
    articles = {}
    for url in urls:
        feed = feedparser.parse(url)
        if feed.entries:
            entry = feed.entries[0]
            header = entry.title
            body = entry.summary
            articles[url] = ArticleContent(header=header, body=body)
        else:
            articles[url] = ArticleContent(header="No entries found", body="")
    return articles

