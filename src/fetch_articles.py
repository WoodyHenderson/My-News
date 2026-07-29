from dataclasses import dataclass

@dataclass
class ArticleContent:
    header: str
    body: str

def fetch_articles(urls: list[str]) -> dict[str, ArticleContent]:
   """"""

