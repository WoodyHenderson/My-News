from __future__ import annotations

from dataclasses import dataclass, field

from src.models.article_content import ArticleContent


@dataclass
class RankedArticle:
    article: ArticleContent
    score: float
    matched_interests: list[str] = field(default_factory=list)  # interest IDs that contributed to the score
