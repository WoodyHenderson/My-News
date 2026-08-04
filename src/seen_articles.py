import sqlite3

conn = sqlite3.connect("seen_articles.db")
cursor = conn.cursor()

cursor.execute ("""
CREATE TABLE IF NOT EXISTS seen_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    title TEXT,
    seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

