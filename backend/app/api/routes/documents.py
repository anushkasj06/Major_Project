"""Document upload and management routes."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
import os, shutil, uuid, httpx
from datetime import datetime
from app.core.security import get_current_user, get_current_admin
from app.core.config import settings
from app.core.database import get_collection
from bson import ObjectId

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    college_id: Optional[str] = Form(None),
    college_name: Optional[str] = Form(None),
    document_type: str = Form("general"),
    current_user=Depends(get_current_admin)
):
    ext = file.filename.split(".")[-1].lower()
    if ext not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail=f"File type .{ext} not allowed")
    if file.size and file.size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    doc = {
        "filename": unique_name,
        "original_filename": file.filename,
        "file_type": ext,
        "file_size": os.path.getsize(file_path),
        "college_id": college_id,
        "college_name": college_name,
        "document_type": document_type,
        "status": "pending",
        "uploaded_by": str(current_user["_id"]),
        "file_path": file_path,
        "created_at": datetime.utcnow(),
    }
    col = get_collection("documents")
    result = await col.insert_one(doc)
    doc_id = str(result.inserted_id)

    # Trigger AI ingestion async
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{settings.AI_SERVICE_URL}/ai/ingest",
                json={"document_id": doc_id, "file_path": file_path, "college_id": college_id, "document_type": document_type}
            )
    except Exception:
        pass  # Will be retried

    return {"document_id": doc_id, "status": "pending", "message": "Upload successful, indexing started"}

@router.get("/")
async def list_documents(current_user=Depends(get_current_admin)):
    col = get_collection("documents")
    cursor = col.find({}).sort("created_at", -1).limit(50)
    docs = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        docs.append(doc)
    return docs

@router.get("/{doc_id}/status")
async def get_document_status(doc_id: str, current_user=Depends(get_current_user)):
    col = get_collection("documents")
    doc = await col.find_one({"_id": ObjectId(doc_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": doc["status"], "chunk_count": doc.get("chunk_count", 0), "error": doc.get("error_message")}
