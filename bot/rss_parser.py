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
    """Scrapes actual news summary from webpage metadata tags."""
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
        response = requests.get(feed_url, impersonate="chrome120", timeout=15)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
        else:
            logging.warning(f"HTTP {response.status_code} for {feed_url}")
    except Exception as e:
        logging.warning(f"Direct fetch failed for {feed_url}: {e}")

    if not feed or not feed.entries:
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            logging.error(f"Fallback feedparser failed for {feed_url}: {e}")
            return []

    if not feed or not feed.entries:
        return []

    for entry in feed.entries:
        # 1. DATE FILTER: Skip any news older than 24 hours
        if not is_recent_article(entry, max_hours=24):
            continue

        title = entry.get("title", "").strip()
        link = entry.get("link", "")

        summary = ""
        if "summary" in entry and entry.summary:
            summary = entry.summary
        elif "description" in entry and entry.description:
            summary = entry.description
        elif "content" in entry and len(entry.content) > 0:
            summary = entry.content[0].value

        # Clean HTML tags
        if summary:
            summary = BeautifulSoup(summary, "html.parser").get_text(separator=" ").strip()

        # If summary matches title, clear it
        if summary.lower() == title.lower():
            summary = ""

        # Fetch actual webpage summary if summary is missing or too short
        if not summary or len(summary) < 20:
            web_summary = fetch_meta_description(link)
            if web_summary:
                summary = web_summary

        search_blob = f"{title} {summary}"

        if matches_keywords(search_blob):
            filtered_articles.append({
                "title": title,
                "summary": summary.strip(),
                "link": link
            })

    return filtered_articles
