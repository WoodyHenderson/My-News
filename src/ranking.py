from __future__ import annotations

from pathlib import Path

import yaml

from src.models.article_content import ArticleContent
from src.models.ranked_article import RankedArticle

_DEFAULT_CONFIG = Path("config/config.yaml")


def rank_articles(
    articles: dict[str, ArticleContent],
    config_path: Path = _DEFAULT_CONFIG,
) -> dict[str, RankedArticle]:
    ranked_articles = {}
    for url, article in articles.items():
        score, matched_interests = score_article(article, config_path)
        ranked_articles[url] = RankedArticle(article=article, score=score, matched_interests=matched_interests)
    return ranked_articles

def score_article(article: ArticleContent, config_path: Path = _DEFAULT_CONFIG) -> tuple[float, list[str]]:
    """
    We are going to use a slightly bastardised version of the BM25 algorithm to score 
    articles based on the interests we have defined in our configuration file.
    BM25 formula: score = sum((IDF * (k + 1) * tf) / (tf + k * (1 - b + b * (dl / avgdl)))) for each term in the query
    where:
        IDF = log((N - n + 0.5) / (n + 0.5) + 1) not Israel Defence Force
        N = total number of documents
        n = number of documents containing the term
        tf = term frequency in the document
        dl = document length
        avgdl = average document length
        k and b are parameters we can tinker with but they are usually 
        chosen as k=1.2 and b=0.6, which we will use here.
    Then, once thats done we apply priority boost and recency bonus to the score.
    """

    