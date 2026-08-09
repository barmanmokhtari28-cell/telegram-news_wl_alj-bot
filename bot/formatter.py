from bs4 import BeautifulSoup

def clean_html(html_content: str) -> str:
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ").strip()

def format_caption(title_fa: str, body_fa: str, link: str, hashtag: str, source_text: str) -> str:
    clean_body = clean_html(body_fa)
    
    if len(clean_body) > 3200:
        clean_body = clean_body[:3197] + "..."

    caption = (
        f"<b>{title_fa}</b>\n\n"
        f"<blockquote expandable>{clean_body}</blockquote>\n\n"
        f"<a href=\"{link}\">{source_text}</a>\n\n"
        f"📰 @secretollah\n"
        f"{hashtag}"
    )
    return caption
