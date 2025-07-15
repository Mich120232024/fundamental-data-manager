from fastapi import APIRouter, Depends, HTTPException
from app.services.auth import get_current_user

router = APIRouter()


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "user_id": current_user.get("sub"),
        "name": current_user.get("name"),
        "email": current_user.get("email"),
        "preferred_username": current_user.get("preferred_username")
    }


@router.post("/validate")
async def validate_token(current_user: dict = Depends(get_current_user)):
    """Validate authentication token"""
    return {
        "valid": True,
        "user_id": current_user.get("sub")
    }