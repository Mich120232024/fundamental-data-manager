from fastapi import APIRouter, Depends
from app.services.auth import get_current_user

router = APIRouter()


@router.get("/")
async def get_layouts(current_user: dict = Depends(get_current_user)):
    """Get user layouts"""
    return {"layouts": []}


@router.post("/")
async def save_layout(layout_data: dict, current_user: dict = Depends(get_current_user)):
    """Save user layout"""
    return {"success": True}