"""
Arambh Backend — Authentication Routes
"""
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from typing import Optional
import logging

from app.models.models import UserCreate, UserLogin, UserRole
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    get_current_user
)
from app.repositories.user_repository import UserRepository
from app.core.redis_client import cache_set, cache_get, cache_delete

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user."""
    existing = await UserRepository.get_by_email(user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_pw = hash_password(user_data.password)
    user_doc = {
        "name": user_data.name,
        "email": user_data.email,
        "hashed_password": hashed_pw,
        "role": UserRole.USER,
        "is_active": True,
        "preferred_language": "en",
        "created_at": datetime.utcnow(),
    }
    user_id = await UserRepository.create(user_doc)

    access_token = create_access_token({"sub": user_id, "role": UserRole.USER})
    refresh_token = create_refresh_token({"sub": user_id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": user_data.name,
            "email": user_data.email,
            "role": UserRole.USER,
        }
    }


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with email and password."""
    user = await UserRepository.get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("is_active"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    user_id = str(user["_id"])
    await UserRepository.update_last_login(user_id)

    access_token = create_access_token({"sub": user_id, "role": user.get("role", "user")})
    refresh_token = create_refresh_token({"sub": user_id})

    # Cache refresh token
    await cache_set(f"refresh:{user_id}", refresh_token, ttl=7 * 24 * 3600)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "user"),
            "preferred_language": user.get("preferred_language", "en"),
        }
    }


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Get new access token using refresh token."""
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    cached = await cache_get(f"refresh:{user_id}")
    if cached != refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

    user = await UserRepository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_access_token = create_access_token({"sub": user_id, "role": user.get("role", "user")})
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(current_user=Depends(get_current_user)):
    """Logout — invalidate refresh token."""
    user_id = str(current_user["_id"])
    await cache_delete(f"refresh:{user_id}")
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    """Get current user profile."""
    return {
        "id": str(current_user["_id"]),
        "name": current_user["name"],
        "email": current_user["email"],
        "role": current_user.get("role", "user"),
        "preferred_language": current_user.get("preferred_language", "en"),
        "created_at": current_user.get("created_at"),
    }


@router.put("/me/language")
async def update_language(language: str, current_user=Depends(get_current_user)):
    """Update preferred language."""
    if language not in ["en", "hi", "mr"]:
        raise HTTPException(status_code=400, detail="Language must be 'en', 'hi', or 'mr'")
    user_id = str(current_user["_id"])
    await UserRepository.update_language(user_id, language)
    return {"message": f"Language updated to {language}"}
