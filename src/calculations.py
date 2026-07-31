from normalise import normalise_for_matching
from src.models.article_content import ArticleContent

def _bm25_tf(tf: int, dl: int, avgdl: float, k: float = 1.2, b: float = 0.6) -> float:
    """
    Calculate the BM25 term frequency score for a term in a document.
    """
    if avgdl == 0:
        return float(tf) # Don't divide by 0
    return ((k + 1) * tf) / (tf + k * (1 - b + b * (dl / avgdl))) # Mafs

def calculate_average_doclength(articles: dict[str, ArticleContent]) -> tuple[float, float]:
    """
    Calculate the average document length.
    """
    if not articles:
        return [0.0, 0.0]
    titles = [len(normalise_for_matching(article.title).split()) for article in articles.values()]
    bodies = [len(normalise_for_matching(article.body).split()) for article in articles.values()]
    article_count = len(articles)
    average_titles_length = sum(titles) / article_count
    average_bodies_length = sum(bodies) / article_count

    return average_titles_length, average_bodies_length
