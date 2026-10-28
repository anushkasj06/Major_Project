"""
Embedding service using HuggingFace Sentence Transformers (free, local).
"""
from sentence_transformers import SentenceTransformer
from typing import List
import logging, os

logger = logging.getLogger(__name__)

_model: SentenceTransformer = None
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIMENSION", "384"))


async def init_embeddings():
    global _model
    logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
    _model = SentenceTransformer(EMBEDDING_MODEL)
    logger.info(f"✅ Embedding model loaded (dim={EMBEDDING_DIM})")


def get_embedding_model() -> SentenceTransformer:
    if _model is None:
        raise RuntimeError("Embeddings not initialized")
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embedding_model()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    return embed_texts([query])[0]
