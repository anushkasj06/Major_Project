"""Translation Agent — translates queries and responses for Hindi/Marathi support."""
import logging, os
from typing import Optional
from app.agents.llm_provider import generate_response
from app.prompts.templates import TRANSLATION_PROMPT

logger = logging.getLogger(__name__)

LANG_NAMES = {"en": "English", "hi": "Hindi", "mr": "Marathi"}


async def translate_text(text: str, target_language: str, source_language: str = "en") -> str:
    """Translate text to target language using LLM."""
    if target_language == source_language or target_language == "en":
        return text

    lang_name = LANG_NAMES.get(target_language, target_language)
    prompt = TRANSLATION_PROMPT.format(target_language=lang_name, text=text)

    try:
        translated = await generate_response(prompt)
        return translated.strip()
    except Exception as e:
        logger.warning(f"Translation failed: {e}")
        return text


async def normalize_to_english(text: str, detected_language: str) -> str:
    """Normalize a query in any language to English for retrieval."""
    if detected_language == "en":
        return text
    return await translate_text(text, "en", detected_language)
