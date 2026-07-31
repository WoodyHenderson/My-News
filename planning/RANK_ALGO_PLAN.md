"""
    We are going to use a slightly bastardised version of the BM25 algorithm to score 
    articles based on the interests we have defined in our configuration file.
    BM25 formula: score = sum(((k + 1) * tf) / (tf + k * (1 - b + b * (dl / avgdl)))) for each term in the query
    where:
        tf = term frequency in the document (capped at 3 to stop long articles dominating)
        dl = document length
        avgdl = average document length
        k and b are parameters we can tinker with but they are usually 
        chosen as k=1.2 and b=0.6, which we will use here.
    Then, once thats done we apply priority boost and recency bonus to the score.

    So we need to make a loop that gets all the information we need from the config and
    applies it to each article. Which should look like:

    Pre-loop: build interests_by_id and sources_by_id lookup dicts from config lists.

    For each article:
        Normalise title and body for matching (once, not inside inner loops)
        title_length = len(title.split())  # word count, same as calculate_average_doclength
        body_length  = len(body.split())

        score = 0
        matched_interests = []

        --- Only evaluate interests declared on this article's source ---
        For each interest_id in source["interests"]:
            interest = interests_by_id[interest_id]
            interest_score = 0

            title_phrase_spans = []   # title and body span lists are SEPARATE
            body_phrase_spans  = []   # (their offsets are unrelated strings)

            For each phrase in the interest: (sorted longest first)
                normalise the phrase
                find all title hits, record character spans into title_phrase_spans
                find all body  hits, record character spans into body_phrase_spans
                title_hits = min(count, 3)
                body_hits  = min(count, 3)
                interest_score += interest_weight * phrase_weight * (
                title_weight * bm25_tf(title_hits, title_length, avg_title_length) +
                body_weight  * bm25_tf(body_hits,  body_length,  avg_body_length)
                )

            For each term in the interest:
                normalise the term
                use word-boundary regex to avoid substring false positives (e.g. AI inside "said")
                count title hits NOT overlapping title_phrase_spans -> min(count, 3)
                count body  hits NOT overlapping body_phrase_spans  -> min(count, 3)
                interest_score += interest_weight * term_weight * (
                title_weight * bm25_tf(title_hits, title_length, avg_title_length) +
                body_weight  * bm25_tf(body_hits,  body_length,  avg_body_length)
                )

            if interest_score > 0:   # use interest_score here, not the running total
                matched_interests.append(interest_id)
                score += interest_score

        --- Recency and source boost (only when there is a positive match) ---
        if score > 0:
            recency  = 2.0 * max(0, 1 - age_hours / lookback_hours)  # clamp future dates to 0
            priority = clamp(source["priority_boost"], 0.0, 1.0)
            score   += recency + priority

        store score, matched_interests, and a breakdown dict in RankedArticle

    rank_articles (separate function) then:
        filter score >= minimum_score
        filter within lookback window (drop undated unless --include-undated)
        sort by score descending, published_at descending, normalised title ascending
        return top max_articles
    """