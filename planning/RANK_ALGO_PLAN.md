"""
    We are going to use a slightly bastardised version of the BM25 algorithm to score 
    articles based on the interests we have defined in our configuration file.
    BM25 formula: score = sum(((k + 1) * tf) / (tf + k * (1 - b + b * (dl / avgdl)))) for each term in the query
    where:
        tf = term frequency in the document
        dl = document length
        avgdl = average document length
        k and b are parameters we can tinker with but they are usually 
        chosen as k=1.2 and b=0.6, which we will use here.
    Then, once thats done we apply priority boost and recency bonus to the score.

    So we need to make a loop that gets all the information we need from the config and
    applies it to each article. Which should look like:

    For each article:
        Normalise title and body for matching
        score = 0
        matched_interests = []
        For each interest in the config:
            interest_score = 0
            phrase_spans = []
            For each phrase in the interest: (sorted longest first)
                normalise the phrase
                count title hits, record spans

                count body hits, record spans
                interest_score += interest_weight * phrase_weight * (
                title_weight * bm25_tf(title_hits, title_length, avg_title_length) +
                body_weight  * bm25_tf(body_hits,  body_length,  avg_body_length)
                )
            For each term in the interest:
                normalise the term
                count title hits not in title_phrase_spans
                count body hits not in body_phrase_spans
                interest_score += interest_weight * term_weight * (
                title_weight * bm25_tf(title_hits, title_length, avg_title_length) +
                body_weight  * bm25_tf(body_hits,  body_length,  avg_body_length)
                )
            
            if score is > 0, add matched interests and add to main score counter
        Now we apply the recency bonus and priority boost and return it.

    filter articles where score >= minimum score, sort by score descending, then
    published_at descending then title ascending, return top max_articles.
    """