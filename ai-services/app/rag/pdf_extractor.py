"""PDF text and table extraction utilities."""
import asyncio, logging, os
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


async def extract_pdf_text(file_path: str) -> str:
    """Extract all text from a PDF file."""
    def _extract():
        try:
            import pdfplumber
            texts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    # Extract regular text
                    text = page.extract_text() or ""
                    if text:
                        texts.append(text)
                    # Extract tables as text
                    tables = page.extract_tables() or []
                    for table in tables:
                        rows = []
                        for row in table:
                            if row:
                                rows.append(" | ".join(str(cell or "").strip() for cell in row))
                        if rows:
                            texts.append("\n".join(rows))
            return "\n\n".join(texts)
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}, trying pypdf")
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                return "\n\n".join(
                    page.extract_text() or "" for page in reader.pages
                )
            except Exception as e2:
                logger.error(f"PDF extraction failed: {e2}")
                return ""

    return await asyncio.to_thread(_extract)


async def extract_pdf_metadata(file_path: str) -> Dict[str, Any]:
    """Extract PDF metadata (title, author, subject)."""
    def _meta():
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            meta = reader.metadata or {}
            return {
                "title": meta.get("/Title", ""),
                "author": meta.get("/Author", ""),
                "subject": meta.get("/Subject", ""),
                "pages": len(reader.pages),
            }
        except Exception:
            return {"pages": 0}
    return await asyncio.to_thread(_meta)


async def extract_pdf_tables(file_path: str) -> List[List[List[str]]]:
    """Extract all tables from a PDF as a list of 2D arrays."""
    def _tables():
        try:
            import pdfplumber
            all_tables = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables() or []
                    for table in tables:
                        cleaned = []
                        for row in table:
                            if row:
                                cleaned.append([str(c or "").strip() for c in row])
                        if cleaned:
                            all_tables.append(cleaned)
            return all_tables
        except Exception as e:
            logger.warning(f"Table extraction failed: {e}")
            return []
    return await asyncio.to_thread(_tables)
