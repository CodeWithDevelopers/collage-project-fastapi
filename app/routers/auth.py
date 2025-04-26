from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.user import UserCreate, UserLogin, UsersResponse, UserUpdate, UserOut
from app.schemas.token import Token, TokenRefresh
from app.services.user_service import UserService
from app.core.config import get_database
from app.core.security import (
    verify_password, create_access_token,
    create_refresh_token, decode_token
)
from app.dependencies.auth import get_current_user, get_admin_user

router = APIRouter()
user_service = UserService(get_database())


@router.post("/register", response_model=Dict[str, Any])
async def register(user: UserCreate):
    existing_user = await user_service.get_user_by_email(user.email)
    if existing_user["success"]:
        raise HTTPException(status_code=400, detail="Email already registered.")
    return await user_service.create_user(user.dict())


@router.post("/login", response_model=Dict[str, Any])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await user_service.get_user_by_email(form_data.username)
    if not db_user["success"] or not verify_password(form_data.password, db_user["data"]["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "sub": db_user["data"]["email"],
        "user_id": db_user["data"]["id"],
        "role": db_user["data"].get("role", "user")
    }

    return user_service.build_response(
        success=True,
        message="Login successful",
        data={
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
            "token_type": "bearer"
        }
    )


@router.get("/users/me", response_model=Dict[str, Any])
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return await user_service.get_user_by_id(int(current_user["user_id"]))


@router.get("/admin-only", response_model=Dict[str, Any])
async def admin_only(current_admin: dict = Depends(get_admin_user)):
    return user_service.build_response(True, f"Welcome Admin {current_admin['sub']}", {}, 200)


@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(data: TokenRefresh):
    payload = decode_token(data.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_payload = {
        "sub": payload["sub"],
        "user_id": payload["user_id"],
        "role": payload["role"]
    }

    return user_service.build_response(
        True,
        "Token refreshed",
        {
            "access_token": create_access_token(new_payload),
            "refresh_token": create_refresh_token(new_payload),
            "token_type": "bearer"
        }
    )


@router.get("/users", response_model=Dict[str, Any])
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    sort: Optional[str] = None,
    fields: Optional[str] = None,
    user_service: UserService = Depends(lambda: UserService(get_database()))
):
    users = await user_service.list_users(page=page, limit=limit, sort=sort, fields=fields)
    return user_service.build_response(True, "Users fetched successfully", users)


@router.get("/users/{user_id}", response_model=Dict[str, Any])
async def get_user(user_id: int):
    user = await user_service.get_user_by_id(user_id)
    if not user["success"]:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=Dict[str, Any])
async def update_user(user_id: int, update: UserUpdate):
    return await user_service.update_user(user_id, update.dict(exclude_unset=True))


@router.delete("/users/{user_id}", response_model=Dict[str, Any])
async def delete_user(user_id: int):
    return await user_service.delete_user(user_id)
