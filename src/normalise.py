import html
import re
import unicodedata
import trafilatura

from src.models.article_content import ArticleContent

_PUNCTUATION_TRANSLATION = str.maketrans(
    {
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
    }
)


def _normalise_for_storage(text: str) -> str:
    plain_text = trafilatura.html2txt(f"<html><body>{text}</body></html>")
    plain_text = html.unescape(plain_text)
    plain_text = unicodedata.normalize("NFC", plain_text)
    return re.sub(r"\s+", " ", plain_text).strip()


def normalise_for_matching(text: str) -> str:
    text = html.unescape(text)
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(_PUNCTUATION_TRANSLATION)
    text = text.casefold()
    return re.sub(r"\s+", " ", text).strip()


def normalise_validate_articles(articles: dict[str, ArticleContent]) -> dict[str, ArticleContent]:
    """
    Here we are normalising the articles by cleaning up the input we are receiving from the RSS feeds, e.g. if you use feedparser_test.py
    you can see that the text body is filled with symbols from translation errors between encoding types, so we will do some 
    normalisation here to get rid of that and clear it up before we store it in our database. Unlike the above function,
    which is used for matching and ranking, this is what we are storing.
    """
    normalised_articles = {}
    for url, article in articles.items():
        normalised_articles[url] = ArticleContent(
            title=_normalise_for_storage(article.title),
            body=_normalise_for_storage(article.body),
            source_id=article.source_id,
            published_at=article.published_at,
        )
    return normalised_articles



