"""
Document chunking pipeline — RecursiveCharacterTextSplitter + semantic chunking.
"""
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
import re, os

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "64"))


def chunk_text(
    text: str,
    metadata: Dict[str, Any] = {},
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """Split text into overlapping chunks with metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "।", ".", "!", "?", ",", " ", ""],
        length_function=len,
    )
    raw_chunks = splitter.split_text(clean_text(text))
    chunks = []
    for i, chunk in enumerate(raw_chunks):
        if len(chunk.strip()) < 30:  # Skip very short chunks
            continue
        chunks.append({
            "text": chunk.strip(),
            "chunk_index": i,
            **metadata,
        })
    return chunks


def clean_text(text: str) -> str:
    """Basic text cleaning."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\.,!?\-\(\)\[\]:\;\'\"\n।]', '', text)
    text = text.strip()
    return text


def chunk_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Chunk a list of document dicts, each with 'text' and 'metadata'."""
    all_chunks = []
    for doc in documents:
        chunks = chunk_text(
            doc.get("text", ""),
            metadata={
                "college_id": doc.get("college_id"),
                "college_name": doc.get("college_name"),
                "doc_type": doc.get("doc_type", "general"),
                "source_url": doc.get("source_url"),
                "source_file": doc.get("source_file"),
                "metadata": doc.get("metadata", {}),
            }
        )
        all_chunks.extend(chunks)
    return all_chunks
