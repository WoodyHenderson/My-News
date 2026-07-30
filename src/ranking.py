from models.article_content import ArticleContent
from src.models.ranked_article import RankedArticle

def rank_articles(articles: dict[str, ArticleContent]) -> dict[str, RankedArticle]:
    
    ranked_articles = {}
    for url in articles:
        article = articles[url]
        matched_interests = []
        
    return ranked_articles

def score_article(article: ArticleContent, matched_interests: list[str]) -> float:
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
    score = 0.0
    
    