# Scoring Analysis: How to Proceed with `score_articles`

_Generated from codebase analysis on 2026-07-31._

## Formula Decision

Use **BM25** as defined in `RANK_ALGO_PLAN.md` — this supersedes the logarithmic formula in `DETAILED_PLAN.md §14.3`. BM25 is already implemented in `calculations.py` and is the newer decision. Retain all behavioral requirements from `DETAILED_PLAN.md`: word-boundary matching, phrase overlap suppression, occurrence caps, exclusions, required terms, recency, source boosts, explainability, and deterministic ordering.

Update `DETAILED_PLAN.md §14.3` to note BM25 as the chosen formula when next revisiting the plan.

---

## Blockers to Fix Before Extending `score_articles`

### 1. `config["interests"]` is a list, not a mapping

The current code calls `.items()` on interests, which will fail at runtime. Iterate over the list instead:

```python
for interest in config["interests"]:
    interest_id = interest["id"]
```

### 2. `source_id` carries the feed URL, not the configured source ID

`fetch_articles.py` stores the feed URL in `ArticleContent.source_id`. Priority boosts and per-source interest restrictions are keyed by configured IDs like `bbc-front-page`. Pass source configuration into fetching so both the source ID and URL are preserved.

### 3. `config_run.py` fetches zero articles

```python
urls = config_data.get("url", [])  # BUG: should read from sources list
```

URLs live inside `config_data["sources"]`. Fix to extract enabled source URLs:

```python
sources = [s for s in config_data.get("sources", []) if s.get("enabled", True)]
```

### 4. `RankedArticle` cannot hold an explanation or rejection reason

Extend the model to carry the breakdown needed for explainability and the `explain` command:

```python
@dataclass
class RankedArticle:
    article: ArticleContent
    score: float
    matched_interests: list[str]
    score_breakdown: dict  # lexical contributions, recency, source_priority, total
    rejected: bool = False
    rejection_reason: str | None = None
```

### 5. `body` conflates summary and full article text

`ArticleContent.body` can be an RSS summary or full extracted text. This prevents applying the planned field weights (`summary=2.0`, `content_text=0.75`) accurately. For now, treat `body` uniformly at weight `2.0`. Longer term, split into `summary` and `content_text` fields.

---

## Recommended `score_articles` Implementation Order

### Step 1 — Initialise lookups

```python
interests_by_id = {i["id"]: i for i in config["interests"]}
sources_by_id   = {s["id"]: s for s in config["sources"]}
```

### Step 2 — Calculate corpus averages once

```python
avg_title_length, avg_body_length = calculate_average_doclength(articles)
```

### Step 3 — Per-article loop

For each article:

1. Look up its source config via `article.source_id`.
2. Normalise title and body once: `title = normalise_for_matching(article.title)`.
3. Compute token lengths: `title_len = len(title.split())` etc.

### Step 4 — Exclusion check (early exit)

Before evaluating any interest, check all `excluded` values across all active interests. A boundary-aware match in either field should mark the article ineligible immediately:

```python
pattern = re.compile(rf"(?<!\w){re.escape(normalise_for_matching(excl))}(?!\w)")
```

### Step 5 — Per-interest loop (restricted to source's declared interests)

Only evaluate interests listed in `source["interests"]`:

```python
for interest_id in source.get("interests", []):
    interest = interests_by_id.get(interest_id)
```

### Step 6 — `required_any` gate

If `required_any` is non-empty and none of those terms match either field, skip this interest (but allow another interest to qualify the article).

### Step 7 — Phrase matching (longest first)

Sort phrases by descending length before iterating. Maintain **separate** span lists for title and body — they are independent strings:

```python
title_phrase_spans: list[tuple[int, int]] = []
body_phrase_spans:  list[tuple[int, int]] = []
```

For each phrase match, record the character spans so component terms can be suppressed.

### Step 8 — Term matching (boundary-aware, span-suppressed)

```python
pattern = re.compile(rf"(?<!\w){re.escape(normalise_for_matching(term))}(?!\w)")
```

Discard any match whose span overlaps a previously recorded phrase span in the same field.

### Step 9 — BM25 contribution with occurrence cap

Cap each accepted occurrence count at **3** before passing to `_bm25_tf`. Field weights:

| Field | Weight |
|-------|-------:|
| Title | 4.0 |
| Body  | 2.0 |

$$
M = W_{\text{interest}} \times W_{\text{value}} \times \left(4.0 \cdot \text{BM25}(tf_t, dl_t, \overline{dl_t}) + 2.0 \cdot \text{BM25}(tf_b, dl_b, \overline{dl_b})\right)
$$

### Step 10 — Accumulate interest score

Add `interest_id` to `matched_interests` only when `interest_score > 0`. Add to the article's running `score`.

### Step 11 — Recency and source boost (only after a positive lexical match)

```python
if score > 0:
    age_hours = (now - article.published_at).total_seconds() / 3600
    recency = 2.0 * max(0.0, 1.0 - age_hours / lookback_hours)
    priority = min(max(source.get("priority_boost", 0.0), 0.0), 1.0)
    score += recency + priority
```

Clamp future-dated articles so recency contribution cannot exceed `2.0`. Pass an aware `now` into the function to keep tests deterministic.

---

## Keep Ranking Separate from Scoring

`score_articles` calculates and explains scores.  
`rank_articles` applies filters and ordering:

1. Reject articles with no positive lexical match.
2. Apply `lookback_hours` (reject undated unless `--include-undated`).
3. Apply `minimum_score`.
4. Sort: score descending → publication time descending → normalised title ascending.
5. Truncate to `max_articles`.
6. _(Later)_ Repeat suppression once storage/emission history exists.

---

## Score Breakdown Format

```json
{
  "total": 31.7,
  "matches": [
    {"interest": "ai", "value": "artificial intelligence", "field": "title", "contribution": 24.0},
    {"interest": "ai", "value": "inference", "field": "body", "contribution": 4.0}
  ],
  "recency": 1.5,
  "source_priority": 0.2
}
```

Store this in `RankedArticle.score_breakdown`. Expose it in the JSON run report and as a concise label in the PDF when `show_match_reasons: true`.

---

## Tests to Write First (Table-Driven)

| Case | Expected outcome |
|------|-----------------|
| `AI` in title | Matches as word; not matched inside `said` |
| `artificial intelligence` in title | Phrase match; `artificial` and `intelligence` term hits suppressed |
| Same phrase in title vs body | Title contributes 4.0×, body 2.0× |
| Term repeated 5 times | Occurrence count capped at 3 |
| Source's interests exclude an interest | That interest not evaluated |
| `required_any` non-empty, none match | Interest skipped; article may still qualify via another interest |
| Excluded phrase matches | Article rejected entirely |
| Recency/source boost with zero lexical score | Bonuses not applied |
| Article older than `lookback_hours` | Filtered by `rank_articles` |
| Undated article | Filtered unless `--include-undated` |
| Equal scores | Tie-broken by date then normalised title |
| Empty articles dict | No division by zero |
