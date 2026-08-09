import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@secretollah")

# Keywords to match (Case-insensitive)
TARGET_KEYWORDS = [
    "iran", "tehran",
    "us", "u.s.", "united states", "washington", "biden",
    "trump", "donald trump"
]

# Direct feeds from outlets
FEEDS = {
    "AlJazeera": {
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "hashtag": "#الجزیره"
    },
    "WSJ": {
        "url": "https://feeds.a1.wsj.net/xml/rss/3_7085.xml",
        "hashtag": "#وال_استریت_جورنال"
    }
}
