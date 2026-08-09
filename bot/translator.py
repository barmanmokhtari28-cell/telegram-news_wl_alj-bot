import logging
from deep_translator import GoogleTranslator

def translate_to_persian(text: str) -> str:
    if not text or not text.strip():
        return ""

    try:
        translator = GoogleTranslator(source='auto', target='fa')
        
        # Free Google Translate API limit is ~5000 characters per request
        max_chunk = 3500
        if len(text) <= max_chunk:
            return translator.translate(text)

        # Chunking mechanism for safety against translation errors
        chunks = [text[i:i + max_chunk] for i in range(0, len(text), max_chunk)]
        translated_chunks = []
        for chunk in chunks:
            translated = translator.translate(chunk)
            if translated:
                translated_chunks.append(translated)
        
        return " ".join(translated_chunks)
    except Exception as e:
        logging.error(f"Error during translation: {e}")
        return text  # Fallback to original text if translation fails
