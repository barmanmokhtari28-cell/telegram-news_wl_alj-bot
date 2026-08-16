import feedparser
import re
import logging
import calendar
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from curl_cffi import requests
from .config import TARGET_KEYWORDS

def matches_keywords(text: str) -> bool:
    if not text:
        return False
    pattern = re.compile(r'\b(' + '|'.join([re.escape(k) for k in TARGET_KEYWORDS]) + r')\b', re.IGNORECASE)
    return bool(pattern.search(text))

def is_recent_article(entry, max_hours=48) -> bool:
    """Discards articles published older than 48 hours."""
    pub_struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if not pub_struct:
        return True

    try:
        pub_time_utc = datetime.fromtimestamp(calendar.timegm(pub_struct), tz=timezone.utc)
        now_utc = datetime.now(timezone.utc)
        return (now_utc - pub_time_utc) <= timedelta(hours=max_hours)
    except Exception as e:
        logging.debug(f"Date parsing error: {e}")
        return True

def fetch_meta_description(url: str) -> str:
    """Fetches full article summary directly from WSJ/AlJazeera webpage metadata."""
    try:
        res = requests.get(url, impersonate="chrome120", timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for attr, val in [
                ("name", "article.summary"),
                ("property", "og:description"),
                ("name", "twitter:description"),
                ("name", "description")
            ]:
                tag = soup.find("meta", attrs={attr: val})
                if tag and tag.get("content"):
                    desc = tag["content"].strip()
                    if desc and len(desc) > 15:
                        return desc
    except Exception as e:
        logging.debug(f"Failed to fetch meta description for {url}: {e}")
    return ""

def fetch_latest_news(feed_url: str) -> list:
    filtered_articles = []
    feed = None

    try:
        response = requests.get(
            feed_url, 
            impersonate="chrome120", 
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=15
        )
        if response.status_code == 200:
            if "just a moment" in response.text.lower() or "<title>challenge" in response.text.lower():
                logging.warning(f"Cloudflare challenge detected for {feed_url}")
            else:
                feed = feedparser.parse(response.content)
        else:
            logging.warning(f"HTTP {response.status_code} for {feed_url}")
    except Exception as e:
        logging.warning(f"curl_cffi fetch failed for {feed_url}: {e}")

    # Fallback to feedparser
    if not feed or not feed.entries:
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            logging.error(f"Fallback feedparser failed for {feed_url}: {e}")
            return []

    if not feed or not feed.entries:
        logging.info(f"0 entries found in feed: {feed_url}")
        return []

    logging.info(f"Fetched {len(feed.entries)} entries from feed: {feed_url}")

    for entry in feed.entries:
        if not is_recent_article(entry, max_hours=48):
            continue

        raw_title = entry.get("title", "").strip()
        title = raw_title.replace(" - The Wall Street Journal", "").replace(" - WSJ", "").strip()
        link = entry.get("link", "")

        summary = ""
        if "summary" in entry and entry.summary:
            summary = entry.summary
        elif "description" in entry and entry.description:
            summary = entry.description
        elif "content" in entry and len(entry.content) > 0:
            summary = entry.content[0].value

        if summary:
            summary = BeautifulSoup(summary, "html.parser").get_text(separator=" ").strip()

        if summary.lower() == title.lower():
            summary = ""

        # If summary is missing, fetch full metadata directly from article URL
        if not summary or len(summary) < 20:
            web_summary = fetch_meta_description(link)
            if web_summary:
                summary = web_summary

        search_blob = f"{title} {summary}"

        if matches_keywords(search_blob):
            logging.info(f"Matched article: '{title}' from {feed_url}")
            filtered_articles.append({
                "title": title,
                "summary": summary.strip(),
                "link": link
            })

    return filtered_articles
