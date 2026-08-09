import feedparser
import re
from .config import TARGET_KEYWORDS

def matches_keywords(text: str) -> bool:
    if not text:
        return False
    pattern = re.compile(r'\b(' + '|'.join([re.escape(k) for k in TARGET_KEYWORDS]) + r')\b', re.IGNORECASE)
    return bool(pattern.search(text))

def fetch_latest_news(feed_url: str) -> list:
    feed = feedparser.parse(feed_url)
    filtered_articles = []

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
