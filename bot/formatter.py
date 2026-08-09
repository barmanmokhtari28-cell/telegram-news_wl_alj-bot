from bs4 import BeautifulSoup

def clean_html(html_content: str) -> str:
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ").strip()

def format_caption(title_fa: str, body_fa: str, link: str, hashtag: str, source_text: str) -> str:
    clean_title = clean_html(title_fa)
    clean_body = clean_html(body_fa)
    
    # Check if there is a real summary different from the title
    has_valid_summary = clean_body and (clean_body.strip().lower() != clean_title.strip().lower())

    if len(clean_body) > 3200:
        clean_body = clean_body[:3197] + "..."

    if has_valid_summary:
        caption = (
            f"<b>{clean_title}</b>\n\n"
            f"<blockquote expandable>{clean_body}</blockquote>\n\n"
            f"<a href=\"{link}\">{source_text}</a>\n\n"
            f"📰 @secretollah\n"
            f"{hashtag}"
        )
    else:
        # If no summary exists, do not render expandable blockquote
        caption = (
            f"<b>{clean_title}</b>\n\n"
            f"<a href=\"{link}\">{source_text}</a>\n\n"
            f"📰 @secretollah\n"
            f"{hashtag}"
        )

    return caption
