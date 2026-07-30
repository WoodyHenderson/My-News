from dataclasses import dataclass
from datetime import datetime

@dataclass
class ArticleContent:
    title: str
    summary: str
    content_text: str
    source_id: str
    published_at: datetime | None