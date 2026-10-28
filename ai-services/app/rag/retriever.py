"""
Hybrid retriever — semantic search + BM25 + cross-encoder reranking.
"""
from typing import List, Dict, Any, Optional
import logging, os
from rank_bm25 import BM25Okapi
from app.rag.vector_store import semantic_search
from app.embeddings.embedding_service import embed_query

logger = logging.getLogger(__name__)

TOP_K = int(os.getenv("TOP_K_RETRIEVAL", "5"))
RERANK_K = int(os.getenv("RERANK_TOP_K", "3"))
ALPHA = float(os.getenv("HYBRID_SEARCH_ALPHA", "0.5"))  # 0=BM25 only, 1=dense only

# Lazy-loaded reranker
_reranker = None


def get_reranker():
    global _reranker
    if _reranker is None:
        try:
            from sentence_transformers import CrossEncoder
            _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            logger.info("✅ Cross-encoder reranker loaded")
        except Exception as e:
            logger.warning(f"Reranker not available: {e}")
    return _reranker


def bm25_search(query: str, corpus: List[Dict], top_k: int = 10) -> List[Dict]:
    """BM25 keyword search over a corpus."""
    if not corpus:
        return []
    tokenized = [doc["text"].lower().split() for doc in corpus]
    bm25 = BM25Okapi(tokenized)
    scores = bm25.get_scores(query.lower().split())
    ranked = sorted(zip(scores, corpus), key=lambda x: x[0], reverse=True)
    return [{"bm25_score": s, **doc} for s, doc in ranked[:top_k] if s > 0]


def reciprocal_rank_fusion(dense_results: List[Dict], bm25_results: List[Dict], k: int = 60) -> List[Dict]:
    """Combine dense and BM25 results using Reciprocal Rank Fusion."""
    scores: Dict[str, float] = {}
    docs: Dict[str, Dict] = {}

    for rank, doc in enumerate(dense_results):
        key = doc.get("text", "")[:100]
        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)
        docs[key] = doc

    for rank, doc in enumerate(bm25_results):
        key = doc.get("text", "")[:100]
        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)
        if key not in docs:
            docs[key] = doc

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [docs[key] for key, _ in ranked]


def rerank(query: str, docs: List[Dict], top_k: int = RERANK_K) -> List[Dict]:
    """Use cross-encoder to rerank retrieved docs."""
    reranker = get_reranker()
    if reranker is None or len(docs) <= 1:
        return docs[:top_k]
    pairs = [(query, doc["text"]) for doc in docs]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
    return [{"rerank_score": float(s), **doc} for s, doc in ranked[:top_k]]


async def retrieve(
    query: str,
    top_k: int = TOP_K,
    college_id: Optional[str] = None,
    use_reranker: bool = True,
) -> List[Dict[str, Any]]:
    """Full hybrid retrieval pipeline."""
    # Dense retrieval
    query_vec = embed_query(query)
    dense_results = await semantic_search(
        query_embedding=query_vec,
        top_k=top_k * 2,
        college_id=college_id,
    )

    # BM25 over dense results (efficient hybrid without full corpus scan)
    bm25_results = bm25_search(query, dense_results, top_k=top_k * 2)

    # Fuse results
    fused = reciprocal_rank_fusion(dense_results, bm25_results)[:top_k * 2]

    # Rerank
    if use_reranker and len(fused) > 1:
        fused = rerank(query, fused, top_k=top_k)
    else:
        fused = fused[:top_k]

    return fused
