from __future__ import annotations

from pathlib import Path
import re

import yaml

from src.models.article_content import ArticleContent
from src.models.ranked_article import RankedArticle
from normalise import normalise_for_matching

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
    """
    This function is here to rank articles after they have been scored, will return a dict
    of url: RankedArticle object, which contains ArticleContent, score, and matched_interests.
    """
    ranked_articles = {}

def score_articles(articles: dict[str, ArticleContent], config_path: Path = _DEFAULT_CONFIG) -> dict[str, RankedArticle]:
    """
    Scores every article based on the configuration file and returns a dict of url : RankedArticle
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    k = 1.2; b = 0.6
    score = 0.0

    ranked_articles = {}
    for url, article in articles.items():
        matched_interests = []
        title = normalise_for_matching(article.title)
        body = normalise_for_matching(article.body)
        score = 0.0
        for interest_id, interest in config["interests"].items():
            interest_score = 0.0
            phrase_spans = []
            for phrase, weight in interest.get("phrases", {}).items():
                phrase = normalise_for_matching(phrase)
                phrase_title_count = title.count(phrase)
                phrase_body_count = body.count(phrase)
                