"""
LLM provider with fallback: Gemini (primary) → Groq (fallback) → OpenAI (optional).
"""
import os, logging, asyncio
from typing import AsyncGenerator, Optional

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PRIMARY_PROVIDER = os.getenv("PRIMARY_LLM_PROVIDER", "gemini")
PRIMARY_MODEL = os.getenv("PRIMARY_LLM_MODEL", "gemini-1.5-flash")
FALLBACK_MODEL = os.getenv("FALLBACK_LLM_MODEL", "llama-3.1-8b-instant")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))


async def generate_response(prompt: str, system: str = "", stream: bool = False) -> str:
    """Generate response with automatic fallback."""
    if PRIMARY_PROVIDER == "gemini" and GEMINI_API_KEY:
        try:
            return await _gemini_generate(prompt, system)
        except Exception as e:
            logger.warning(f"Gemini failed: {e}, falling back to Groq")

    if GROQ_API_KEY:
        try:
            return await _groq_generate(prompt, system)
        except Exception as e:
            logger.warning(f"Groq failed: {e}")

    raise RuntimeError("All LLM providers failed. Check API keys.")


async def stream_response(prompt: str, system: str = "") -> AsyncGenerator[str, None]:
    """Stream tokens from the LLM."""
    if PRIMARY_PROVIDER == "gemini" and GEMINI_API_KEY:
        try:
            async for token in _gemini_stream(prompt, system):
                yield token
            return
        except Exception as e:
            logger.warning(f"Gemini stream failed: {e}")

    if GROQ_API_KEY:
        try:
            async for token in _groq_stream(prompt, system):
                yield token
            return
        except Exception as e:
            logger.warning(f"Groq stream failed: {e}")

    yield "I'm currently unable to process your request. Please try again later."


async def _gemini_generate(prompt: str, system: str = "") -> str:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(PRIMARY_MODEL, system_instruction=system or None)
    response = await asyncio.to_thread(model.generate_content, prompt,
        generation_config=genai.GenerationConfig(max_output_tokens=MAX_TOKENS, temperature=TEMPERATURE))
    return response.text


async def _gemini_stream(prompt: str, system: str = "") -> AsyncGenerator[str, None]:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(PRIMARY_MODEL, system_instruction=system or None)

    def _sync_stream():
        return model.generate_content(prompt, stream=True,
            generation_config=genai.GenerationConfig(max_output_tokens=MAX_TOKENS, temperature=TEMPERATURE))

    response = await asyncio.to_thread(_sync_stream)
    for chunk in response:
        if chunk.text:
            yield chunk.text


async def _groq_generate(prompt: str, system: str = "") -> str:
    from groq import AsyncGroq
    client = AsyncGroq(api_key=GROQ_API_KEY)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = await client.chat.completions.create(
        model=FALLBACK_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )
    return response.choices[0].message.content


async def _groq_stream(prompt: str, system: str = "") -> AsyncGenerator[str, None]:
    from groq import AsyncGroq
    client = AsyncGroq(api_key=GROQ_API_KEY)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    stream = await client.chat.completions.create(
        model=FALLBACK_MODEL, messages=messages,
        max_tokens=MAX_TOKENS, temperature=TEMPERATURE, stream=True
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
