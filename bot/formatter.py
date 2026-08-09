from bs4 import BeautifulSoup

def clean_html(html_content: str) -> str:
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ").strip()

def format_caption(title_fa: str, body_fa: str, link: str, hashtag: str) -> str:
    clean_body = clean_html(body_fa)
    
    # Safe limit to stay below Telegram message boundary (~4096 characters)
    if len(clean_body) > 3200:
        clean_body = clean_body[:3197] + "..."

    # Telegram HTML Rich Text with Expandable Blockquote
    caption = (
        f"<b>{title_fa}</b>\n\n"
        f"<blockquote expandable>{clean_body}</blockquote>\n\n"
        f"🔗 <a href=\"{link}\">مشاهده منبع خبر</a>\n\n"
        f"📰 @secretollah\n"
        f"{hashtag}"
    )
    return caption
