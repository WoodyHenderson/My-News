from __future__ import annotations

import sqlite3
import urllib.parse


def db_connect() -> sqlite3.Connection:
    return sqlite3.connect("seen_articles.db")

def create_tables() -> None:
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_articles (
                canonical_url TEXT PRIMARY KEY
            )
            """
        )
        conn.commit()

def mark_seen(url: str) -> bool:
    create_tables()
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO seen_articles (canonical_url) VALUES (?)",
            (canonicalise_url(url),),
        )
        conn.commit()
        return cursor.rowcount > 0

def canonicalise_url(url: str) -> str:
    """
    Canonicalise a URL for storage in the database
    """
    url = url.strip()
    parts = urllib.parse.urlsplit(url)
    cleaned = parts._replace(
        scheme=parts.scheme.lower(),
        netloc=parts.netloc.lower(),
        fragment="",
    )
    rebuilt = urllib.parse.urlunsplit(cleaned)
    return rebuilt