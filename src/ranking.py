from __future__ import annotations

from pathlib import Path

import yaml

from src.models.article_content import ArticleContent
from src.models.ranked_article import RankedArticle

_DEFAULT_CONFIG = Path("config/config.yaml")

def _bm25_tf(tf: int, dl: int, avgdl: float, k: float = 1.2, b: float = 0.6) -> float:
    """
    Calculate the BM25 term frequency score for a term in a document.
    """
    if avgdl == 0:
        return float(tf) # Don't divide by 0
    return ((k + 1) * tf) / (tf + k * (1 - b + b * (dl / avgdl))) # Mafs

def rank_articles(
    articles: dict[str, ArticleContent],
    config_path: Path = _DEFAULT_CONFIG,
) -> dict[str, RankedArticle]:
    ranked_articles = {}
    for url, article in articles.items():
        score, matched_interests = score_articles(articles, config_path)
        ranked_articles[url] = RankedArticle(article=article, score=score, matched_interests=matched_interests)
    return ranked_articles

def score_articles(articles: dict[str, ArticleContent], config_path: Path = _DEFAULT_CONFIG) -> tuple[float, list[str]]:
    """
    The planning for this took forever and got very long so see RANK_ALGO_PLAN.md if u want 
    insight into how we got here.
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    k = 1.2; b = 0.6
    score = 0.0
    matched_interests = []

    for interest in config.get("interests", []):

    