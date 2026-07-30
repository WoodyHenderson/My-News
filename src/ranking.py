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
    Our YAML config weighs interests, e.g. each source (every url) has a corresponding priority boost,
    this is mostly weighted towards the front page of each as since these are quite generalised its 
    hard to catch important things with the specific interests.
    Then we have interests which will make up the majority of our scoring, e.g. if an article
    has a phrase or term that is in the config we add the weight (we will also do some normalisation)
    e.g. diminishing returns for repeated phrases, we will also bias towards the header, so if a header
    has a phrase or term that is in the config we will add more weight than if it was in the body.
    We will also have to normalise for the length of the article, e.g. if an article is 10,000 words long 
    and has a phrase in it once, it should be less important than if an article is 100 words long and has the 
    same phrase in it once. The priority boost will be a multiplier at the end.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    interests = config.get("interests", [])
    diminished_values = [1, 0.5, 0.25]
    matched_interests = []
    score = 0.0
    for word in article.header:
        for interest in interests:
            count = article.header.count(interest)
            if count > 0:
                matched_interests.append(interest)
                score += 
        