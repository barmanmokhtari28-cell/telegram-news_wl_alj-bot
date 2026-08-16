import logging
import asyncio
import os
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

from bot.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, FEEDS
from bot.database import init_db, is_article_posted, mark_article_posted
from bot.rss_parser import fetch_latest_news
from bot.translator import translate_to_persian
from bot.formatter import format_caption
from bot.video_downloader import download_news_video

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
                logging.info(f"Skipping already posted article: {article['title']}")
                continue

            logging.info(f"New relevant article found from {source}: {article['title']}")

            title_fa = translate_to_persian(article["title"])
            summary_fa = translate_to_persian(article["summary"])

            is_video_link = "/video/" in link or "video" in article["title"].lower()
            video_path = None

            if is_video_link:
                logging.info(f"Attempting video download for {link}...")
                video_path = download_news_video(link)

            posted_successfully = False

            if video_path and os.path.exists(video_path):
                formatted_video_message = format_caption(
                    title_fa=title_fa,
                    body_fa=summary_fa,
                    link=link,
                    hashtag=data["hashtag"],
                    source_text=data["source_text"],
                    is_video=True
                )
                try:
                    with open(video_path, 'rb') as video_file:
                        await bot.send_video(
                            chat_id=TELEGRAM_CHANNEL_ID,
                            video=video_file,
                            caption=formatted_video_message,
                            parse_mode=ParseMode.HTML
                        )
                    logging.info(f"Successfully posted video: {link}")
                    posted_successfully = True
                except TelegramError as e:
                    logging.error(f"Failed to send video, falling back to text: {e}")
                finally:
                    if os.path.exists(video_path):
                        try:
                            os.remove(video_path)
                        except Exception:
                            pass

            if not posted_successfully:
                formatted_text_message = format_caption(
                    title_fa=title_fa,
                    body_fa=summary_fa,
                    link=link,
                    hashtag=data["hashtag"],
                    source_text=data["source_text"],
                    is_video=False
                )
                try:
                    await bot.send_message(
                        chat_id=TELEGRAM_CHANNEL_ID,
                        text=formatted_text_message,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=False
                    )
                    logging.info(f"Successfully posted text: {link}")
                    posted_successfully = True
                except TelegramError as e:
                    logging.error(f"Telegram API Error: {e}")

            if posted_successfully:
                mark_article_posted(link)
                await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run_once())
