"""Document service — handles upload, status tracking, re-indexing."""
import os, shutil, uuid
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import UploadFile
from app.core.config import settings
from app.core.database import get_collection


class DocumentService:

    @staticmethod
    async def save_upload(
        file: UploadFile,
        uploaded_by: str,
        college_id: Optional[str] = None,
        college_name: Optional[str] = None,
        document_type: str = "general",
    ) -> Dict[str, Any]:
        ext = file.filename.split(".")[-1].lower() if file.filename else "bin"
        if ext not in settings.ALLOWED_FILE_TYPES:
            raise ValueError(f"File type .{ext} not allowed. Allowed: {settings.ALLOWED_FILE_TYPES}")

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        unique_name = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_name)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        file_size = os.path.getsize(file_path)
        if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            os.remove(file_path)
            raise ValueError(f"File too large. Max {settings.MAX_FILE_SIZE_MB}MB")

        doc = {
            "filename": unique_name,
            "original_filename": file.filename,
            "file_type": ext,
            "file_size": file_size,
            "college_id": college_id,
            "college_name": college_name,
            "document_type": document_type,
            "status": "pending",
            "chunk_count": 0,
            "uploaded_by": uploaded_by,
            "file_path": file_path,
            "created_at": datetime.utcnow(),
        }
        col = get_collection("documents")
        result = await col.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return doc

    @staticmethod
    async def mark_indexed(document_id: str, chunk_count: int):
        from bson import ObjectId
        col = get_collection("documents")
        await col.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"status": "indexed", "chunk_count": chunk_count, "indexed_at": datetime.utcnow()}}
        )

    @staticmethod
    async def mark_failed(document_id: str, error: str):
        from bson import ObjectId
        col = get_collection("documents")
        await col.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"status": "failed", "error_message": error}}
        )
