# PDF Digest Generation Plan

## 1. Goal

Generate the ranked news digest as an A4 PDF by:

1. Preparing a small presentation context from the ranked article data.
2. Rendering `src/pdf/digest.html` with Jinja2.
3. Applying `src/pdf/style.css` as print CSS.
4. Converting the rendered HTML to PDF with WeasyPrint.
5. Writing the result safely to the requested or configured output path.

The digest is an index of stories, not a copy of the articles. Do not include `ArticleContent.body` in the HTML or PDF.

## 2. Current State

The required dependencies are already declared in `pyproject.toml`:

- `Jinja2>=3.1.4`
- `weasyprint>=69.0`
- `pypdf>=5.0.0` as an optional development dependency

The three PDF files currently exist but are empty:

- `src/pdf/generate_pdf.py`
- `src/pdf/digest.html`
- `src/pdf/style.css`

The ranker returns this shape:

```python
list[tuple[str, RankedArticle]]
```

Each tuple contains:

- The article URL.
- A `RankedArticle` containing `article`, `score`, and `matched_interests`.

The nested `ArticleContent` provides `title`, `body`, `source_id`, and optional `published_at`.

`src/commands/config_run.py` already calls `generate_pdf(ranked_articles, output_path)`, but it should eventually pass the digest configuration and report the path returned by the PDF function.

## 3. Rendering Contract

Keep the Jinja template focused on presentation. Convert each `(url, RankedArticle)` pair into a simple story dictionary before rendering.

Suggested story fields:

```python
{
    "rank": 1,
    "url": "https://example.com/story",
    "title": "Story title",
    "source_id": "bbc-front-page",
    "published_iso": "2026-08-01T10:30:00+00:00",
    "published_label": "01 Aug 2026, 10:30",
    "score_label": "12.5",
    "matched_interests": ["gaming", "ai"],
}
```

Suggested document-level fields:

```python
{
    "title": "My News",
    "generated_iso": "2026-08-01T12:00:00+01:00",
    "generated_label": "01 August 2026 at 12:00 BST",
    "stories": [...],
    "story_count": 12,
    "show_match_reasons": True,
}
```

Prepare formatted dates in Python instead of placing substantial date logic in Jinja. Use `zoneinfo.ZoneInfo` with the configured `digest.timezone` when displaying dates.

Only permit `http` and `https` story URLs. Jinja autoescaping protects HTML text, but it does not by itself make an unsafe URL scheme safe.

## 4. Implement `generate_pdf.py`

### 4.1 Create the Jinja environment

Use a file-system loader rooted at `Path(__file__).parent`, where the template and stylesheet live.

Configure:

- `FileSystemLoader` for `digest.html`.
- `select_autoescape(("html", "xml"))` so titles and source names are escaped.
- `StrictUndefined` so missing template fields fail immediately instead of silently producing incomplete output.

### 4.2 Build the context

Add a small helper such as:

```python
def build_digest_context(
    ranked_articles: Sequence[tuple[str, RankedArticle]],
    digest_config: Mapping[str, object],
    generated_at: datetime,
) -> dict[str, object]:
    ...
```

Responsibilities:

- Preserve the order returned by `rank_articles`.
- Number stories from 1.
- Format dates in the configured timezone.
- Format scores consistently.
- Include match labels only when `show_match_reasons` is enabled.
- Never copy `article.body` into the context.

### 4.3 Decide the output path

Use this precedence:

1. The CLI `--output` value, when supplied.
2. Otherwise, combine `digest.output_directory` and `digest.filename` from the YAML configuration.
3. Replace `{date}` in the configured filename with the local digest date in `YYYY-MM-DD` form.

Create the parent directory with `mkdir(parents=True, exist_ok=True)`.

Require a `.pdf` suffix or add it when absent. Return the final `Path` from `generate_pdf` so the CLI can print the actual destination.

### 4.4 Render HTML and convert it

The core flow should be:

```python
template = environment.get_template("digest.html")
rendered_html = template.render(context)
HTML(
    string=rendered_html,
    base_url=str(Path(__file__).parent),
).write_pdf(temporary_path)
```

`base_url` is important because it allows WeasyPrint to resolve the relative `style.css` link in `digest.html`.

### 4.5 Write atomically

Do not render directly over an existing digest.

1. Create a temporary PDF in the destination directory.
2. Ask WeasyPrint to write to the temporary path.
3. Confirm the file is non-empty and starts with `%PDF-`.
4. Optionally parse it with `pypdf` in development checks.
5. Replace the destination with `Path.replace()` only after validation succeeds.
6. Delete the temporary file in a `finally` block after any failure.

This preserves an existing valid digest if rendering fails halfway through.

### 4.6 Proposed public function

Use a signature along these lines:

```python
def generate_pdf(
    ranked_articles: Sequence[tuple[str, RankedArticle]],
    output_path: Path | None = None,
    *,
    digest_config: Mapping[str, object] | None = None,
) -> Path:
    ...
```

Keeping `output_path` as the second argument remains compatible with the existing call while allowing configuration to be added explicitly.

## 5. Build `digest.html`

Use semantic HTML with these sections:

- `<head>` with UTF-8 metadata, the document title, and `<link rel="stylesheet" href="style.css">`.
- A header containing the digest title, generated date, and story count.
- An ordered list containing one `<article>` per story.
- A linked `<h2>` headline.
- Source, publication date, and score metadata.
- Optional matched-interest labels.
- A short empty state if no stories are supplied.

The main loop will follow this shape:

```jinja2
{% for story in stories %}
  <li class="story">
    <span class="rank">{{ story.rank }}</span>
    <article>
      <h2><a href="{{ story.url }}">{{ story.title }}</a></h2>
      ...
    </article>
  </li>
{% endfor %}
```

Do not use the `safe` filter on feed-provided data. Let Jinja escape headlines and other external text.

Do not render:

- `article.body`
- Scraped article content
- Images from remote publishers
- Raw HTML from feeds

## 6. Build `style.css`

Create print-focused CSS rather than browser-only styling.

Required rules:

- `@page { size: A4; ... }` with stable margins.
- Page number and digest date in bottom margin boxes.
- A high-contrast, locally available font stack.
- Clear visual hierarchy for the title, rank, headline, and metadata.
- `break-inside: avoid` on each story.
- `orphans` and `widows` rules for readable page breaks.
- `overflow-wrap: anywhere` for unusually long headlines and URLs.
- Underlined links that remain recognizable in grayscale.
- Compact spacing so a useful number of stories fit on each page.

Do not depend on a web font or remote asset. Local fonts make PDF generation deterministic and avoid network requests during rendering.

## 7. Connect the Renderer to the Command

Update `src/commands/config_run.py` after the renderer is complete:

```python
pdf_path = generate_pdf(
    ranked_articles,
    output_path,
    digest_config=config_data.get("digest", {}),
)
typer.secho(f"Successfully generated PDF at {pdf_path}", fg="green")
```

This fixes the current success message, which prints `None` when no explicit output path was supplied.

The Typer `run` command in `src/cli.py` currently validates the configuration and then stops. For complete end-to-end generation, it must hand off to `run_application` rather than ending after validation. Keep that CLI wiring as a separate final integration step so the PDF renderer can first be checked in isolation.

## 8. Manual Smoke Check

After implementing the three PDF files, create one synthetic `RankedArticle` and call `generate_pdf` directly. The check should confirm:

1. The returned file exists and is non-empty.
2. Its first bytes are `%PDF-`.
3. It opens in Preview on macOS.
4. The headline, source, date, score, and matched interests appear.
5. The headline link opens the expected external URL.
6. The article body does not appear.
7. A headline containing `&`, `<`, or non-ASCII text renders correctly.
8. A long headline wraps without leaving the page.

A useful automated version can use `pypdf.PdfReader` to extract text and inspect link annotations, but it is optional for the first implementation.

## 9. Implementation Order

1. Verify `jinja2` and `weasyprint` import in the active virtual environment.
2. Define the renderer signature and context builder in `generate_pdf.py`.
3. Render `digest.html` to an HTML string and inspect it with one synthetic story.
4. Add the semantic Jinja template with autoescaped fields.
5. Add A4 print CSS and confirm `base_url` resolves it.
6. Add WeasyPrint conversion and atomic output handling.
7. Run the manual smoke check with one story, then with enough stories for multiple pages.
8. Pass the digest configuration from `config_run.py` and print the returned path.
9. Wire `cli.py` to `run_application` for end-to-end use.
10. Add concise usage instructions to `README.md` once the command works.

## 10. Completion Criteria

The PDF work is complete when:

- A valid PDF is generated from the ranker's existing tuple output.
- Story ordering exactly matches the ranker output.
- Headlines are clickable and external text is escaped.
- Article bodies are absent.
- The configured title, timezone, output directory, and filename are honored.
- CLI `--output` overrides the configured path.
- Multi-page output has stable A4 layout and page numbers.
- A failed render cannot overwrite an existing valid PDF.
- The CLI reports the real generated path.
