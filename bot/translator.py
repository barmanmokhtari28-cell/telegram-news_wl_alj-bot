import logging
from deep_translator import GoogleTranslator

def is_error_page(text: str) -> bool:
    """Checks if the translated text is an error message from Google."""
    if not text:
        return False
    error_keywords = [
        "error 500", 
        "server error", 
        "500.that’s an error", 
        "there was an error", 
        "please try again later"
    ]
    return any(keyword in text.lower() for keyword in error_keywords)

def translate_to_persian(text: str) -> str:
    if not text or not text.strip():
        return ""

    try:
        translator = GoogleTranslator(source='auto', target='fa')
        max_chunk = 3000
        
        # Short text translation
        if len(text) <= max_chunk:
            translated = translator.translate(text)
            if translated and not is_error_page(translated):
                return translated
            logging.warning("Google Translate returned an error page. Falling back to original text.")
            return text  # Fallback to original English text

        # Long text translation (chunking)
        chunks = [text[i:i + max_chunk] for i in range(0, len(text), max_chunk)]
        translated_chunks = []
        for chunk in chunks:
            translated = translator.translate(chunk)
            if translated and not is_error_page(translated):
                translated_chunks.append(translated)
            else:
                translated_chunks.append(chunk)
        
        result = " ".join(translated_chunks)
        if is_error_page(result):
            return text
            
        return result

    except Exception as e:
        logging.error(f"Error during translation: {e}")
        return text  # Fallback to original English text if translation fails
