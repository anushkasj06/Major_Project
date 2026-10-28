"""Tests for RAG pipeline components."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def test_chunk_text_basic():
    from app.rag.chunker import chunk_text
    text = "Engineering colleges in Maharashtra provide excellent education. " * 30
    chunks = chunk_text(text, metadata={"college_id": "test123", "doc_type": "general"})
    assert len(chunks) > 0
    for chunk in chunks:
        assert "text" in chunk
        assert len(chunk["text"].strip()) >= 30
        assert chunk["college_id"] == "test123"


def test_chunk_text_with_devanagari():
    from app.rag.chunker import chunk_text
    text = "महाराष्ट्रातील अभियांत्रिकी महाविद्यालये उत्कृष्ट शिक्षण देतात. " * 20
    chunks = chunk_text(text, metadata={})
    assert len(chunks) > 0


def test_clean_text():
    from app.rag.chunker import clean_text
    dirty = "  Hello    World   \n\n  Test   "
    result = clean_text(dirty)
    assert "  " not in result
    assert result.strip() == result


@pytest.mark.asyncio
async def test_rag_pipeline_no_docs():
    """When no docs are retrieved, response should say so."""
    with patch("app.agents.rag_agent.retrieve", AsyncMock(return_value=[])), \
         patch("app.agents.rag_agent.analyze_query", AsyncMock(return_value={
             "intent": "general", "entities": {}, "language": "en",
             "cleaned_query": "test query", "requires_comparison": False
         })):
        from app.agents.rag_agent import run_rag_pipeline
        result = await run_rag_pipeline(
            query="test query", session_id="sess1", user_id="user1"
        )
        assert "response" in result
        assert len(result["response"]) > 0


def test_language_detection():
    from app.agents.query_agent import detect_language
    assert detect_language("What are the fees?") == "en"
    assert detect_language("COEP की फीस क्या है?") == "hi"


def test_format_history():
    from app.memory.conversation_memory import format_history
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
    ]
    result = format_history(messages)
    assert "USER" in result or "user" in result.lower()
    assert "Hello" in result


def test_fee_pattern_extraction():
    from app.utils.text_cleaner import extract_fees_pattern
    text = "Annual tuition fee is ₹95,000 per year. Hostel charges are Rs. 60,000 annually."
    fees = extract_fees_pattern(text)
    assert len(fees) >= 1


def test_placement_pattern_extraction():
    from app.utils.text_cleaner import extract_placement_pattern
    text = "Average package is 9.2 LPA. Highest package is 48 LPA. 91% students placed."
    result = extract_placement_pattern(text)
    assert result.get("avg_lpa") == 9.2
    assert result.get("highest_lpa") == 48.0
    assert result.get("placement_pct") == 91.0
