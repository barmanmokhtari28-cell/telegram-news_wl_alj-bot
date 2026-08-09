import feedparser
import urllib.request
import re
import logging
from .config import TARGET_KEYWORDS

# Full browser headers to bypass WSJ 403 Forbidden block
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none'
}

def matches_keywords(text: str) -> bool:
    if not text:
        return False
    pattern = re.compile(r'\b(' + '|'.join([re.escape(k) for k in TARGET_KEYWORDS]) + r')\b', re.IGNORECASE)
    return bool(pattern.search(text))

def fetch_latest_news(feed_url: str) -> list:
    filtered_articles = []
    feed = None

    # Strategy 1: Fetch using urllib with full browser headers
    try:
        req = urllib.request.Request(feed_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read()
            feed = feedparser.parse(xml_data)
    except Exception as e:
        logging.warning(f"urllib fetch failed for {feed_url}: {e}. Trying feedparser fallback...")

    # Strategy 2: Fallback to feedparser direct fetch
    if not feed or not feed.entries:
        try:
            feed = feedparser.parse(
                feed_url, 
                agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
        except Exception as e:
            logging.error(f"Failed to parse feed {feed_url}: {e}")
            return []

    if not feed or not feed.entries:
        logging.warning(f"No entries found for feed: {feed_url}")
        return []

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
