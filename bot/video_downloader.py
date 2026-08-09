import os
import logging
import yt_dlp

TEMP_VIDEO_PATH = "data/temp_video.mp4"

def download_news_video(url: str) -> str | None:
    """Downloads video using yt-dlp if under 45MB."""
    if os.path.exists(TEMP_VIDEO_PATH):
        try:
            os.remove(TEMP_VIDEO_PATH)
        except Exception:
            pass

    ydl_opts = {
        'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'outtmpl': TEMP_VIDEO_PATH,
        'quiet': True,
        'no_warnings': True,
        'max_filesize': 45 * 1024 * 1024,  # 45MB limit for Telegram API
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(TEMP_VIDEO_PATH) and os.path.getsize(TEMP_VIDEO_PATH) > 0:
            return TEMP_VIDEO_PATH
    except Exception as e:
        logging.debug(f"Video download not available for {url}: {e}")
        if os.path.exists(TEMP_VIDEO_PATH):
            try:
                os.remove(TEMP_VIDEO_PATH)
            except Exception:
                pass

    return None
