"""Integration test: fetch The Guardian RSS feed and parse articles with trafilatura fallback."""
import feedparser
import requests
import trafilatura
import truststore

# Inject macOS system Keychain trust (required on corporate networks with SSL inspection)
truststore.inject_into_ssl()

GUARDIAN_RSS_URL = "https://www.theguardian.com/uk/rss"


def test_guardian_feed_parse_and_extract(capsys):
    response = requests.get(GUARDIAN_RSS_URL, timeout=15)
    response.raise_for_status()
    feed = feedparser.parse(response.text)

    assert feed.entries, "Guardian RSS feed returned no entries — check URL or network"

    for entry in feed.entries[:3]:  # limit to first 3 to keep test fast
        title = entry.get("title", "(no title)")
        summary = entry.get("summary", "")
        link = entry.get("link", "")

        if not summary and link:
            downloaded = trafilatura.fetch_url(link)
            if downloaded:
                summary = trafilatura.extract(downloaded) or ""

        print(f"\n--- {title} ---")
        print(f"URL:  {link}")
        print(f"Body: {summary[:300]}{'...' if len(summary) > 300 else ''}")

    with capsys.disabled():
        print(f"\n\nParsed {len(feed.entries)} entries from Guardian RSS.")
