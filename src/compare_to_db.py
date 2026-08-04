from src.models.ranked_article import RankedArticle
from src.seen_articles import is_seen

def compare_to_seen(ranked_articles: list[tuple[str, RankedArticle]]) -> list[tuple[str, RankedArticle]]:
    """
    Compare the ranked articles against seen articles stored in the database and 
    filter out seen articles, then we just return the updated filtered list.
    """

    filtered_articles = []
    for url, ranked_article in ranked_articles:
        if not is_seen(url):
            filtered_articles.append((url, ranked_article))
    return filtered_articles
            