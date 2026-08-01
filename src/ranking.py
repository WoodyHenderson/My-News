from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
import yaml

from src.models.article_content import ArticleContent
from src.models.ranked_article import RankedArticle
from normalise import normalise_for_matching
from calculations import _bm25_tf, calculate_average_doclength

_DEFAULT_CONFIG = Path("config/config.yaml")

def overlaps(span: tuple[int, int], spans: list[tuple[int, int]]) -> bool:
    """
    Check if a span overlaps with any of the spans in a list of spans.
    """
    s, e = span
    for s2, e2 in spans:
        if s < e2 and s2 < e:
            return True
    return False

def rank_articles(
    articles: dict[str, ArticleContent],
    config_path: Path = _DEFAULT_CONFIG,
) -> list[tuple[str, RankedArticle]]:
    """
    This function is here to rank articles after they have been scored, will return a dict
    of url: RankedArticle object, which contains ArticleContent, score, and matched_interests.
    """
    ranked_articles = score_articles(articles, config_path)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    digest = config.get("digest", {})
    minimum_score = digest.get("minimum_score", 1.0)
    max_articles = digest.get("max_articles", 30)

    above_minimum = []
    for url, r in ranked_articles.items():
        if r.score >= minimum_score:
            above_minimum.append((url, r))

    def sort_key(item: tuple[str, RankedArticle]):
        url, ranked = item
        published = ranked.article.published_at

        if published is not None:
            timestamp = -published.timestamp()
        else:
            timestamp = 0

        return (-ranked.score, timestamp, normalise_for_matching(ranked.article.title))

    above_minimum.sort(key=sort_key)
    return above_minimum[:max_articles]

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

    now = datetime.now(timezone.utc)

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
            # Sort by longest to shortest to ensure shorter phrases that are included
            # in longer phrases don't get double counted.
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
                # Dont ask me how this regex works, copilot wrote it
                pattern = re.compile(rf"(?<!\w){re.escape(term)}(?!\w)") 

                title_matches = list(pattern.finditer(title))
                body_matches = list(pattern.finditer(body))

                title_tf = min(
                    sum(
                        1 # increment by 1 if no overlaps with existing phrase spans
                        for match in title_matches
                        if not overlaps(match.span(), title_phrase_spans)
                    ),
                    3 # max of 3
                )
                body_tf = min(
                    sum(
                        1
                        for match in body_matches
                        if not overlaps(match.span(), body_phrase_spans)
                    ),
                    3
                )

                interest_score += interest_weight * term_weight * (
                    4.0 * _bm25_tf(title_tf, title_length, avg_title_length) +
                    2.0 * _bm25_tf(body_tf, body_length, avg_body_length)
                )

            if interest_score > 0:
                matched_interests.append(interest_id)
                score += interest_score

        if score > 0:
            source = sources_by_id.get(article.source_id, {})
            if article.published_at is not None:
                age_hours = (now - article.published_at).total_seconds() / 3600
                lookback_hours = config.get("digest", {}).get("lookback_hours", 48)
                recency = 2.0 * max(0.0, 1.0 - age_hours / lookback_hours)
                score += recency
            priority = min(max(source.get("priority_boost", 0.0), 0.0), 1.0) # copilot was smart here and suggested this as a fix for a potential edge case if someone is an idiot
            score += priority
        ranked_articles[url] = RankedArticle(
            article=article,
            score=score,
            matched_interests=matched_interests
        )
    return ranked_articles
