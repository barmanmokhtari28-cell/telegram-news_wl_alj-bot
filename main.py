import logging
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

from bot.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, FEEDS
from bot.database import init_db, is_article_posted, mark_article_posted
from bot.rss_parser import fetch_latest_news
from bot.translator import translate_to_persian
from bot.formatter import format_caption

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def run_once():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        logging.error("TELEGRAM_BOT_TOKEN or TELEGRAM_CHANNEL_ID missing.")
        return

    init_db()
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    logging.info("Checking news feeds...")

    for source, data in FEEDS.items():
        articles = fetch_latest_news(data["url"])
        
        for article in reversed(articles):
            link = article["link"]
            
            if is_article_posted(link):
                continue

            logging.info(f"New relevant article found from {source}: {article['title']}")

            title_fa = translate_to_persian(article["title"])
            summary_fa = translate_to_persian(article["summary"])

            formatted_message = format_caption(
                title_fa=title_fa,
                body_fa=summary_fa,
                link=link,
                hashtag=data["hashtag"],
                source_text=data["source_text"]
            )

            try:
                await bot.send_message(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    text=formatted_message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=False
                )
                mark_article_posted(link)
                logging.info(f"Successfully posted: {link}")
                await asyncio.sleep(2)

            except TelegramError as e:
                logging.error(f"Telegram API Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_once())
