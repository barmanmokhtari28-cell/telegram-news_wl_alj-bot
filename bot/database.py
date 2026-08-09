import sqlite3
import os

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
DB_NAME = os.path.join(DATA_DIR, "posted_news.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posted_articles (
            link TEXT PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()

def is_article_posted(link: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM posted_articles WHERE link = ?", (link,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_article_posted(link: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO posted_articles (link) VALUES (?)", (link,))
    conn.commit()
    conn.close()
