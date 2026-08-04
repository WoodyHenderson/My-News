from src.seen_articles import is_seen
from src.models.article_content import ArticleContent

def compare_to_seen(article_data: dict[str, ArticleContent]) -> dict[str, ArticleContent]:
    """
    Compare the ranked articles against seen articles stored in the database and 
    filter out seen articles, then we just return the updated filtered list.
    """

    filtered_articles = []
    for url, ranked_article in article_data.items():
        if not is_seen(url):
            filtered_articles.append((url, ranked_article))
    return dict(filtered_articles)
            