import feedparser
import re
import logging
from bs4 import BeautifulSoup
from curl_cffi import requests
from .config import TARGET_KEYWORDS

def matches_keywords(text: str) -> bool:
    if not text:
        return False
    pattern = re.compile(r'\b(' + '|'.join([re.escape(k) for k in TARGET_KEYWORDS]) + r')\b', re.IGNORECASE)
    return bool(pattern.search(text))

def fetch_meta_description(url: str) -> str:
    """Fetches full article summary directly from WSJ/AlJazeera webpage metadata if RSS summary is too short."""
    try:
        res = requests.get(url, impersonate="chrome120", timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            og_desc = soup.find("meta", property="og:description")
            if og_desc and og_desc.get("content"):
                return og_desc["content"].strip()
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                return meta_desc["content"].strip()
    except Exception as e:
        logging.debug(f"Failed to fetch webpage meta description for {url}: {e}")
    return ""

def fetch_latest_news(feed_url: str) -> list:
    filtered_articles = []
    feed = None

    # Direct fetch using browser TLS impersonation
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
        logging.warning(f"No entries found for feed: {feed_url}")
        return []

    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "")

        summary = ""
        if "content" in entry and len(entry.content) > 0:
            summary = entry.content[0].value
        else:
            summary = entry.get("summary", "") or entry.get("description", "")

        # Clean HTML tags
        if summary:
            summary = BeautifulSoup(summary, "html.parser").get_text(separator=" ").strip()

        search_blob = f"{title} {summary}"

        if matches_keywords(search_blob):
            # If summary is missing or too short, scrape full webpage summary
            if not summary or len(summary) < 30:
                web_summary = fetch_meta_description(link)
                if web_summary:
                    summary = web_summary

            filtered_articles.append({
                "title": title,
                "summary": summary if summary else title,
                "link": link
            })

    return filtered_articles
