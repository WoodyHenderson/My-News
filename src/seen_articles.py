from __future__ import annotations

import sqlite3
import urllib.parse


def db_connect() -> sqlite3.Connection:
    return sqlite3.connect("seen_articles.db")


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
    canonical_url = canonicalise_url(url)
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO seen_articles (canonical_url) VALUES (?)",
            (canonical_url,),
        )
        conn.commit()
        return cursor.rowcount > 0

def is_seen(url: str) -> bool:
    create_tables()
    canonical_url = canonicalise_url(url)
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM seen_articles WHERE canonical_url = ?",
            (canonical_url,),
        )
        if cursor.fetchone():
            return True
        return False