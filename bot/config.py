import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@secretollah")

TARGET_KEYWORDS = [
    "iran", "tehran",
    "us", "u.s.", "united states", "washington", "biden",
    "trump", "donald trump"
]

FEEDS = {
    "AlJazeera": {
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "hashtag": "#الجزیره",
        "source_text": "الجــزیــره 🇶🇦"
    },
    "WSJ_World": {
        "url": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
        "hashtag": "#وال_استریت_جورنال",
        "source_text": "وال استریت ژورنال  🇺🇸  "
    },
    "WSJ_Politics": {
        "url": "https://feeds.a.dj.com/rss/WSJcomUSPolitics.xml",
        "hashtag": "#وال_استریت_جورنال",
        "source_text": "وال استریت ژورنال  🇺🇸  "
    }
}
