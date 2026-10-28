"""Document ingestion pipeline — PDF, DOCX, TXT extraction → chunk → embed → index."""
import os, logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


async def extract_text_from_file(file_path: str) -> str:
    """Extract text from PDF, DOCX, or TXT files."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return await _extract_pdf(file_path)
    elif ext == ".docx":
        return await _extract_docx(file_path)
    elif ext in [".txt", ".md", ".csv"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {ext}")


async def _extract_pdf(file_path: str) -> str:
    import asyncio
    def _sync():
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                pages = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text)
                return "\n\n".join(pages)
        except Exception:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    return await asyncio.to_thread(_sync)


async def _extract_docx(file_path: str) -> str:
    import asyncio
    def _sync():
        from docx import Document
        doc = Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
    return await asyncio.to_thread(_sync)


async def ingest_file(
    document_id: str,
    file_path: str,
    college_id: Optional[str] = None,
    document_type: str = "general",
    college_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Full ingestion pipeline for a local file."""
    from app.rag.chunker import chunk_text
    from app.rag.vector_store import upsert_chunks
    from app.rag.ingestion import extract_text_from_file

    logger.info(f"Ingesting file: {file_path}")

    # Extract text
    text = await extract_text_from_file(file_path)
    if not text.strip():
        return {"status": "failed", "error": "No text extracted", "chunk_count": 0}

    # Chunk
    chunks = chunk_text(text, metadata={
        "college_id": college_id,
        "college_name": college_name,
        "doc_type": document_type,
        "source_file": os.path.basename(file_path),
        "document_id": document_id,
    })

    # Upsert to vector store
    count = await upsert_chunks(chunks)

    # Update document status in MongoDB
    try:
        import motor.motor_asyncio
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/arambh")
        client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
        db = client[os.getenv("MONGODB_DB_NAME", "arambh")]
        from bson import ObjectId
        await db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"status": "indexed", "chunk_count": count, "indexed_at": datetime.utcnow()}}
        )
        client.close()
    except Exception as e:
        logger.warning(f"Could not update document status: {e}")

    logger.info(f"✅ Ingested {count} chunks from {file_path}")
    return {"status": "indexed", "chunk_count": count, "document_id": document_id}


async def ingest_url(url: str, college_id: Optional[str] = None, college_name: Optional[str] = None) -> Dict:
    """Ingest content from a URL."""
    import httpx
    from app.rag.chunker import chunk_text
    from app.rag.vector_store import upsert_chunks
    import trafilatura

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, headers={"User-Agent": "ArambhBot/1.0"})
        response.raise_for_status()
        html = response.text

    text = trafilatura.extract(html, include_tables=True, include_links=False) or ""
    if not text.strip():
        return {"status": "failed", "error": "No text extracted from URL"}

    chunks = chunk_text(text, metadata={
        "college_id": college_id,
        "college_name": college_name,
        "doc_type": "web",
        "source_url": url,
    })
    count = await upsert_chunks(chunks)
    return {"status": "indexed", "chunk_count": count, "url": url}
