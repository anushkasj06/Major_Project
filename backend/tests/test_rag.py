"""Tests for RAG pipeline."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_retrieve_returns_results():
    mock_docs = [
        {"text": "COEP fees for CSE is ₹95,000 per year.", "score": 0.92,
         "college_name": "COEP", "source_url": "https://coep.org.in/fees", "doc_type": "fees"}
    ]
    with patch("app.rag.retriever.semantic_search", AsyncMock(return_value=mock_docs)), \
         patch("app.embeddings.embedding_service.embed_query", return_value=[0.1]*384):
        from app.rag.retriever import retrieve
        results = await retrieve("What are COEP fees?", top_k=3)
        assert len(results) >= 1
        assert "text" in results[0]


def test_chunker_basic():
    from app.rag.chunker import chunk_text
    text = "Engineering colleges in Pune. COEP was established in 1854. " * 20
    chunks = chunk_text(text, metadata={"college_id": "123"})
    assert len(chunks) > 0
    for chunk in chunks:
        assert len(chunk["text"]) > 0
        assert chunk["college_id"] == "123"


def test_language_detection():
    from app.agents.query_agent import detect_language
    assert detect_language("What are the fees for COEP?") == "en"
    assert detect_language("COEP की फीस क्या है?") == "hi"
    assert detect_language("COEP ची फी किती आहे?") == "mr"
