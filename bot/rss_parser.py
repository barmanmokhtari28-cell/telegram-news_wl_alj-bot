import feedparser
import re
import logging
from curl_cffi import requests
from .config import TARGET_KEYWORDS

def matches_keywords(text: str) -> bool:
    if not text:
        return False
    pattern = re.compile(r'\b(' + '|'.join([re.escape(k) for k in TARGET_KEYWORDS]) + r')\b', re.IGNORECASE)
    return bool(pattern.search(text))

def fetch_latest_news(feed_url: str) -> list:
    filtered_articles = []
    feed = None

    # Use curl_cffi to impersonate real Chrome browser TLS fingerprint
    try:
        response = requests.get(feed_url, impersonate="chrome120", timeout=15)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
        else:
            logging.warning(f"HTTP {response.status_code} for {feed_url}")
    except Exception as e:
        logging.warning(f"curl_cffi fetch failed for {feed_url}: {e}. Trying feedparser fallback...")

    # Fallback to feedparser direct
    if not feed or not feed.entries:
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            logging.error(f"Fallback failed for {feed_url}: {e}")
            return []

    if not feed or not feed.entries:
        logging.warning(f"No entries found for feed: {feed_url}")
        return []

    for entry in feed.entries:
        raw_title = entry.get("title", "")
        title = raw_title.replace(" - The Wall Street Journal", "").replace(" - WSJ", "").strip()
        
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
