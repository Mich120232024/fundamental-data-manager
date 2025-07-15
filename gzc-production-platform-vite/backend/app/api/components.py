from fastapi import APIRouter, Depends
from app.services.auth import get_current_user

router = APIRouter()


@router.get("/")
async def get_components(current_user: dict = Depends(get_current_user)):
    """Get available components"""
    return {"components": []}


@router.get("/{component_id}")
async def get_component(component_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific component data"""
    return {"component_id": component_id}