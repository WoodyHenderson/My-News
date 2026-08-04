from datetime import UTC, datetime

from pypdf import PdfReader

from src.models.article_content import ArticleContent
from src.models.ranked_article import RankedArticle
from output_generation.generate_digest import generate_pdf


def test_generate_pdf_sorts_by_score_and_includes_article_details(tmp_path):
    lower_score = RankedArticle(
        article=ArticleContent(
            title="Lower-scored article",
            body="",
            source_id="source-low",
            published_at=None,
        ),
        score=1.25,
    )
    higher_score = RankedArticle(
        article=ArticleContent(
            title="Higher-scored article",
            body="",
            source_id="source-high",
            published_at=datetime(2026, 8, 1, tzinfo=UTC),
        ),
        score=9.5,
        matched_interests=["technology"],
    )
    output_path = tmp_path / "digest.pdf"

    result = generate_pdf(
        [
            ("https://example.com/lower", lower_score),
            ("https://example.com/higher", higher_score),
        ],
        output_path,
        digest_config={"title": "Test Digest"},
    )

    pdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(result).pages)

    assert result == output_path
    assert result.read_bytes().startswith(b"%PDF-")
    assert pdf_text.index("Higher-scored article") < pdf_text.index("Lower-scored article")
    assert "https://example.com/higher" in pdf_text
    assert "https://example.com/lower" in pdf_text
    assert "Score 9.50" in pdf_text
    assert "source-high" in pdf_text
    assert "01 Aug 2026" in pdf_text
    assert "Matched: technology" in pdf_text


def test_generate_pdf_uses_configured_output_path(tmp_path):
    result = generate_pdf(
        [],
        digest_config={
            "output_directory": tmp_path,
            "filename": "my-news-{date}.pdf",
        },
    )

    pdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(result).pages)

    assert result.parent == tmp_path
    assert result.name.startswith("my-news-")
    assert result.suffix == ".pdf"
    assert "No articles matched this edition." in pdf_text