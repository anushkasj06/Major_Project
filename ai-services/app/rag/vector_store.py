"""
Qdrant vector store — hybrid search (dense + BM25 sparse).
"""
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter,
    FieldCondition, MatchValue, SearchRequest, SparseVectorParams,
    SparseIndexParams
)
from typing import List, Dict, Any, Optional
import logging, os, uuid

logger = logging.getLogger(__name__)

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "arambh_docs")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIMENSION", "384"))

_client: AsyncQdrantClient = None


async def init_vector_store():
    global _client
    logger.info(f"Connecting to Qdrant: {QDRANT_URL}")
    _client = AsyncQdrantClient(url=QDRANT_URL)
    collections = await _client.get_collections()
    names = [c.name for c in collections.collections]
    if COLLECTION_NAME not in names:
        await _client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )
        # Create payload indexes for fast filtering
        await _client.create_payload_index(COLLECTION_NAME, "college_id", "keyword")
        await _client.create_payload_index(COLLECTION_NAME, "doc_type", "keyword")
        await _client.create_payload_index(COLLECTION_NAME, "source_url", "keyword")
        logger.info(f"✅ Qdrant collection '{COLLECTION_NAME}' created")
    else:
        logger.info(f"✅ Qdrant collection '{COLLECTION_NAME}' ready")


def get_qdrant() -> AsyncQdrantClient:
    if _client is None:
        raise RuntimeError("Qdrant not initialized")
    return _client


async def upsert_chunks(chunks: List[Dict[str, Any]]) -> int:
    """Upsert document chunks with embeddings into Qdrant."""
    from app.embeddings.embedding_service import embed_texts
    client = get_qdrant()
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)
    points = []
    for chunk, embedding in zip(chunks, embeddings):
        point_id = chunk.get("id") or str(uuid.uuid4())
        points.append(PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "text": chunk["text"],
                "college_id": chunk.get("college_id"),
                "college_name": chunk.get("college_name"),
                "doc_type": chunk.get("doc_type", "general"),
                "source_url": chunk.get("source_url"),
                "source_file": chunk.get("source_file"),
                "chunk_index": chunk.get("chunk_index", 0),
                "metadata": chunk.get("metadata", {}),
            }
        ))
    await client.upsert(collection_name=COLLECTION_NAME, points=points)
    return len(points)


async def semantic_search(
    query_embedding: List[float],
    top_k: int = 5,
    college_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    score_threshold: float = 0.3,
) -> List[Dict[str, Any]]:
    """Perform dense vector similarity search with optional filters."""
    client = get_qdrant()
    query_filter = None
    conditions = []
    if college_id:
        conditions.append(FieldCondition(key="college_id", match=MatchValue(value=college_id)))
    if doc_type:
        conditions.append(FieldCondition(key="doc_type", match=MatchValue(value=doc_type)))
    if conditions:
        from qdrant_client.models import Filter, Must
        query_filter = Filter(must=conditions)

    results = await client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=top_k,
        query_filter=query_filter,
        score_threshold=score_threshold,
    )
    return [
        {
            "text": r.payload.get("text", ""),
            "score": r.score,
            "college_id": r.payload.get("college_id"),
            "college_name": r.payload.get("college_name"),
            "doc_type": r.payload.get("doc_type"),
            "source_url": r.payload.get("source_url"),
            "source_file": r.payload.get("source_file"),
            "metadata": r.payload.get("metadata", {}),
        }
        for r in results
    ]


async def delete_by_college(college_id: str) -> int:
    client = get_qdrant()
    from qdrant_client.models import Filter, FieldCondition, MatchValue, FilterSelector
    result = await client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=FilterSelector(
            filter=Filter(must=[FieldCondition(key="college_id", match=MatchValue(value=college_id))])
        )
    )
    return result.operation_id
