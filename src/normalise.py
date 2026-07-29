from fetch_articles import ArticleContent

def normalise_validate_articles(articles: dict[str, ArticleContent]) -> dict[str, ArticleContent]:
    """
    Here we are normalising the articles by cleaning up the input we are receiving from the RSS feeds, e.g. if you use feedparser_test.py
    you can see that the text body is filled with symbols from translation errors between encoding types, so we will do some 
    normalisation here to get rid of that and clear it up before we store it in our database.
    """

    normalised_articles = {}
    disallowed_chars = ['â', '€', '™', '’', '“', '”', '–']
    for url in articles:
        article = articles[url]
        header = article.header.strip()
        body = article.body.strip()
        # This seems incredibly inefficient but I do what I want
        for char in disallowed_chars:
            header = header.replace(char, "")
            body = body.replace(char, "")
        normalised_articles[url] = ArticleContent(header=header, body=body)

    return normalised_articles
