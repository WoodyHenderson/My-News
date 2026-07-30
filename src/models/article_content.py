from dataclasses import dataclass
from datetime import datetime


@dataclass
class ArticleContent:
    title: str
    body: str
    source_id: str
    published_at: datetime | None