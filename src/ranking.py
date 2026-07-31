from __future__ import annotations

from pathlib import Path
import re
import yaml

from src.models.article_content import ArticleContent
from src.models.ranked_article import RankedArticle
from normalise import normalise_for_matching
from calculations import _bm25_tf, calculate_average_doclength

_DEFAULT_CONFIG = Path("config/config.yaml")

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

    interests_by_id = {interest["id"]: interest for interest in config.get("interests", [])}
    sources_by_id = {source["id"]: source for source in config.get("sources", [])}

    avgdl = calculate_average_doclength(articles)
    avg_title_length, avg_body_length = avgdl

    ranked_articles = {}
    for url, article in articles.items():
        score = 0.0

        title = normalise_for_matching(article.title)
        body = normalise_for_matching(article.body)

        title_length = len(title.split())
        body_length = len(body.split())
        matched_interests = []
        for interest_id in sources_by_id.get(article.source_id, {}).get("interests", []):
            interest = interests_by_id.get(interest_id)
            if interest is None:
                continue
            interest_score = 0.0

            title_phrase_spans = []
            body_phrase_spans = []

            interest_weight = interest.get("weight", 1.0)
            sorted_phrases = sorted(
                interest.get("phrases", {}).items(),
                key=lambda x: len(x[0]), reverse=True
            )
            for phrase, phrase_weight in sorted_phrases:
                phrase = normalise_for_matching(phrase)
                pattern = re.compile(re.escape(phrase))

                title_matches = list(pattern.finditer(title))
                body_matches = list(pattern.finditer(body))

                title_tf = min(len(title_matches), 3)
                body_tf = min(len(body_matches), 3)

                title_phrase_spans.extend([match.span() for match in title_matches])
                body_phrase_spans.extend([match.span() for match in body_matches])

                interest_score += interest_weight * phrase_weight * (
                    4.0 * _bm25_tf(title_tf, title_length, avg_title_length) +
                    2.0 * _bm25_tf(body_tf, body_length, avg_body_length)
                )

            for term, term_weight in interest.get("terms", {}).items():
                term = normalise_for_matching(term)
                pattern = re.compile(re.escape(term))

                title_matches = list(pattern.finditer(title))
                body_matches = list(pattern.finditer(body))

                title_tf = min(len(title_matches), 3)
                body_tf = min(len(body_matches), 3)

                title_phrase_spans.extend([match.span() for match in title_matches])
                body_phrase_spans.extend([match.span() for match in body_matches])

                interest_score += interest_weight * term_weight * (
                    2.0 * _bm25_tf(title_tf, title_length, avg_title_length) +
                    1.0 * _bm25_tf(body_tf, body_length, avg_body_length)
                )

