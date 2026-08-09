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
        "hashtag": "#الجزیره"
    },
    "WSJ_World": {
        "url": "https://feeds.a1.wsj.net/xml/rss/3_7085.xml",
        "hashtag": "#وال_استریت_جورنال"
    },
    "WSJ_US": {
        "url": "https://feeds.a1.wsj.net/xml/rss/3_7014.xml",
        "hashtag": "#وال_استریت_جورنال"
    }
}
