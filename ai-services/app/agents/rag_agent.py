"""
Main RAG orchestration agent using LangGraph.
Coordinates: Query Understanding → Retrieval → Response Generation → Validation
"""
from typing import TypedDict, List, Dict, Any, Optional, AsyncGenerator
from langgraph.graph import StateGraph, END
import logging, json

from app.agents.query_agent import analyze_query
from app.rag.retriever import retrieve
from app.agents.llm_provider import generate_response, stream_response
from app.prompts.templates import SYSTEM_PROMPT, RAG_PROMPT_TEMPLATE
from app.memory.conversation_memory import format_history

logger = logging.getLogger(__name__)
MIN_CONFIDENCE = float(__import__('os').getenv("MIN_CONFIDENCE_SCORE", "0.5"))


class RAGState(TypedDict):
    query: str
    session_id: str
    user_id: str
    language: str
    college_filter: Optional[str]
    conversation_history: List[Dict]
    query_analysis: Dict[str, Any]
    retrieved_docs: List[Dict[str, Any]]
    context: str
    response: str
    sources: List[Dict]
    confidence: float
    error: Optional[str]


async def query_understanding_node(state: RAGState) -> RAGState:
    """Node 1: Analyze query for intent and entities."""
    analysis = await analyze_query(state["query"])
    state["query_analysis"] = analysis
    state["language"] = analysis.get("language", state.get("language", "en"))
    return state


async def retrieval_node(state: RAGState) -> RAGState:
    """Node 2: Retrieve relevant chunks from vector store."""
    analysis = state.get("query_analysis", {})
    college_id = state.get("college_filter") or analysis.get("entities", {}).get("college_id")
    search_query = analysis.get("cleaned_query") or state["query"]

    docs = await retrieve(query=search_query, top_k=5, college_id=college_id)
    state["retrieved_docs"] = docs

    # Build context string
    if docs:
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.get("college_name") or doc.get("source_url") or "Unknown Source"
            context_parts.append(f"[Source {i}: {source}]\n{doc['text']}")
        state["context"] = "\n\n".join(context_parts)
        state["confidence"] = docs[0].get("rerank_score", docs[0].get("score", 0.5))
    else:
        state["context"] = ""
        state["confidence"] = 0.0

    return state


async def response_generation_node(state: RAGState) -> RAGState:
    """Node 3: Generate grounded response."""
    if not state["context"]:
        state["response"] = (
            "I don't have specific information about this in my knowledge base. "
            "Please check the official college website or contact the admissions office directly."
        )
        state["sources"] = []
        return state

    history_str = format_history(state.get("conversation_history", []))
    system = SYSTEM_PROMPT.format(language=state.get("language", "en"))
    prompt = RAG_PROMPT_TEMPLATE.format(
        context=state["context"],
        history=history_str,
        query=state["query"]
    )

    response = await generate_response(prompt, system=system)
    state["response"] = response

    # Build sources list for citations
    seen = set()
    sources = []
    for doc in state["retrieved_docs"]:
        key = doc.get("source_url") or doc.get("college_name") or ""
        if key and key not in seen:
            seen.add(key)
            sources.append({
                "college_name": doc.get("college_name"),
                "source_url": doc.get("source_url"),
                "doc_type": doc.get("doc_type"),
                "relevance": round(doc.get("rerank_score", doc.get("score", 0)), 3)
            })
    state["sources"] = sources[:3]  # Top 3 sources
    return state


async def validation_node(state: RAGState) -> RAGState:
    """Node 4: Validate response confidence and flag if low."""
    if state["confidence"] < MIN_CONFIDENCE and state["retrieved_docs"]:
        disclaimer = "\n\n⚠️ *Note: This information may be incomplete. Please verify with the official college website.*"
        if disclaimer not in state["response"]:
            state["response"] += disclaimer
    return state


def build_rag_graph() -> StateGraph:
    """Build the LangGraph RAG pipeline."""
    graph = StateGraph(RAGState)
    graph.add_node("query_understanding", query_understanding_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("response_generation", response_generation_node)
    graph.add_node("validation", validation_node)

    graph.set_entry_point("query_understanding")
    graph.add_edge("query_understanding", "retrieval")
    graph.add_edge("retrieval", "response_generation")
    graph.add_edge("response_generation", "validation")
    graph.add_edge("validation", END)
    return graph.compile()


# Singleton compiled graph
_rag_graph = None

def get_rag_graph():
    global _rag_graph
    if _rag_graph is None:
        _rag_graph = build_rag_graph()
    return _rag_graph


async def run_rag_pipeline(
    query: str,
    session_id: str,
    user_id: str,
    language: str = "en",
    college_filter: Optional[str] = None,
    conversation_history: List[Dict] = [],
) -> Dict[str, Any]:
    """Run the full RAG pipeline and return result."""
    graph = get_rag_graph()
    initial_state = RAGState(
        query=query, session_id=session_id, user_id=user_id,
        language=language, college_filter=college_filter,
        conversation_history=conversation_history,
        query_analysis={}, retrieved_docs=[], context="",
        response="", sources=[], confidence=0.0, error=None
    )
    result = await graph.ainvoke(initial_state)
    return {
        "response": result["response"],
        "sources": result["sources"],
        "confidence": result["confidence"],
        "intent": result.get("query_analysis", {}).get("intent", "general"),
        "language": result["language"],
    }


async def stream_rag_pipeline(
    query: str,
    session_id: str,
    user_id: str,
    language: str = "en",
    college_filter: Optional[str] = None,
    conversation_history: List[Dict] = [],
) -> AsyncGenerator[Dict, None]:
    """Stream the RAG response token by token."""
    # Run retrieval synchronously first
    analysis = await analyze_query(query)
    college_id = college_filter or analysis.get("entities", {}).get("college_id")
    search_query = analysis.get("cleaned_query") or query

    docs = await retrieve(query=search_query, top_k=5, college_id=college_id)

    # Yield sources metadata first
    sources = []
    if docs:
        seen = set()
        for doc in docs:
            key = doc.get("source_url") or doc.get("college_name") or ""
            if key and key not in seen:
                seen.add(key)
                sources.append({
                    "college_name": doc.get("college_name"),
                    "source_url": doc.get("source_url"),
                    "doc_type": doc.get("doc_type"),
                })

    yield {"type": "sources", "sources": sources[:3]}

    if not docs:
        yield {"type": "token", "content": "I don't have specific information about this. Please check the official college website."}
        return

    context = "\n\n".join(
        f"[Source: {d.get('college_name','Unknown')}]\n{d['text']}" for d in docs
    )
    history_str = format_history(conversation_history)
    system = SYSTEM_PROMPT.format(language=language)
    prompt = RAG_PROMPT_TEMPLATE.format(context=context, history=history_str, query=query)

    async for token in stream_response(prompt, system=system):
        yield {"type": "token", "content": token}

    confidence = docs[0].get("rerank_score", docs[0].get("score", 0.5)) if docs else 0.0
    yield {"type": "metadata", "confidence": round(confidence, 3), "intent": analysis.get("intent")}
