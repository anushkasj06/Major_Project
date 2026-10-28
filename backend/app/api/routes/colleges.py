"""Colleges routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.core.security import get_current_user, get_current_admin
from app.repositories.college_repository import CollegeRepository

router = APIRouter()

@router.get("/")
async def list_colleges(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    college_type: Optional[str] = None,
    city: Optional[str] = None,
):
    filters = {}
    if college_type: filters["college_type"] = college_type
    if city: filters["location.city"] = {"$regex": city, "$options": "i"}
    return await CollegeRepository.search(query=search or "", filters=filters, skip=skip, limit=limit)

@router.get("/{college_id}")
async def get_college(college_id: str):
    college = await CollegeRepository.get_by_id(college_id)
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    return college

@router.post("/", dependencies=[Depends(get_current_admin)])
async def create_college(data: dict):
    college_id = await CollegeRepository.create(data)
    return {"id": college_id, "message": "College created"}

@router.put("/{college_id}", dependencies=[Depends(get_current_admin)])
async def update_college(college_id: str, data: dict):
    updated = await CollegeRepository.update(college_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="College not found")
    return {"message": "Updated"}

@router.delete("/{college_id}", dependencies=[Depends(get_current_admin)])
async def delete_college(college_id: str):
    deleted = await CollegeRepository.delete(college_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="College not found")
    return {"message": "Deleted"}
