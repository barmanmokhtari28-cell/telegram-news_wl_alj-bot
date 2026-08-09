import feedparser
import requests
import re
import logging
from .config import TARGET_KEYWORDS

# Custom headers to bypass WSJ anti-bot/403 blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def matches_keywords(text: str) -> bool:
    if not text:
        return False
    pattern = re.compile(r'\b(' + '|'.join([re.escape(k) for k in TARGET_KEYWORDS]) + r')\b', re.IGNORECASE)
    return bool(pattern.search(text))

def fetch_latest_news(feed_url: str) -> list:
    filtered_articles = []
    
    try:
        # Fetch RSS feed with Browser User-Agent
        response = requests.get(feed_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
    except Exception as e:
        logging.error(f"Failed to fetch RSS feed from {feed_url}: {e}")
        return []

    if not feed.entries:
        logging.warning(f"No entries found for feed: {feed_url}")

    for entry in feed.entries:
        title = entry.get("title", "")
        
        summary = ""
        if "content" in entry and len(entry.content) > 0:
            summary = entry.content[0].value
        else:
            summary = entry.get("summary", "") or entry.get("description", "")

        link = entry.get("link", "")

        search_blob = f"{title} {summary}"
        if matches_keywords(search_blob):
            filtered_articles.append({
                "title": title,
                "summary": summary,
                "link": link
            })

    return filtered_articles
