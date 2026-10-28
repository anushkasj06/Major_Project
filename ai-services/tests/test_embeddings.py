"""Tests for embedding service."""
def test_embed_texts():
    from unittest.mock import MagicMock, patch
    mock_model = MagicMock()
    mock_model.encode.return_value = [[0.1]*384, [0.2]*384]
    with patch("app.embeddings.embedding_service._model", mock_model):
        from app.embeddings.embedding_service import embed_texts
        result = embed_texts(["hello", "world"])
        assert len(result) == 2
        assert len(result[0]) == 384
