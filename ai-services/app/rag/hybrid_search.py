"""
Advanced hybrid search combining dense vectors + BM25 + metadata filtering.
Standalone module that can be used independently.
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class HybridSearchEngine:
    """Manages hybrid search with configurable weights."""

    def __init__(self, dense_weight: float = 0.7, bm25_weight: float = 0.3):
        self.dense_weight = dense_weight
        self.bm25_weight = bm25_weight

    async def search(
        self,
        query: str,
        top_k: int = 5,
        college_id: Optional[str] = None,
        doc_type: Optional[str] = None,
        rerank: bool = True,
    ) -> List[Dict[str, Any]]:
        """Full hybrid search pipeline."""
        from app.embeddings.embedding_service import embed_query
        from app.rag.vector_store import semantic_search
        from app.rag.retriever import bm25_search, reciprocal_rank_fusion, rerank as do_rerank

        # Dense retrieval
        query_vec = embed_query(query)
        dense_results = await semantic_search(
            query_embedding=query_vec,
            top_k=top_k * 3,
            college_id=college_id,
            doc_type=doc_type,
        )

        # BM25 over dense results
        bm25_results = bm25_search(query, dense_results, top_k=top_k * 2)

        # Fuse
        fused = reciprocal_rank_fusion(dense_results, bm25_results)[:top_k * 2]

        # Rerank
        if rerank and len(fused) > 1:
            fused = do_rerank(query, fused, top_k=top_k)
        else:
            fused = fused[:top_k]

        return fused

    def format_for_context(self, results: List[Dict[str, Any]], max_chars: int = 3000) -> str:
        """Format search results into a context string for prompting."""
        parts = []
        total_chars = 0
        for i, doc in enumerate(results, 1):
            source = doc.get("college_name") or doc.get("source_url") or f"Source {i}"
            doc_type = doc.get("doc_type", "")
            header = f"[{i}. {source}" + (f" — {doc_type}" if doc_type else "") + "]"
            text = doc["text"][:800]
            entry = f"{header}\n{text}"
            if total_chars + len(entry) > max_chars:
                break
            parts.append(entry)
            total_chars += len(entry)
        return "\n\n".join(parts)
