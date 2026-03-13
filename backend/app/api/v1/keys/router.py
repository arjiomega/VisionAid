from fastapi import APIRouter, Depends, Query
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.keys.service import APIKeyService


router = APIRouter(prefix="/keys", tags=["keys"])

def get_api_key_service(db: AsyncSession = Depends(get_db)) -> APIKeyService:
    return APIKeyService(db)

@router.get("/list")
async def list_api_keys(
    api_key_service = Depends(get_api_key_service),
    disabled: Optional[bool] = Query(None, description="Filter by disabled status"),
    min_remaining: Optional[int] = Query(None, description="Filter keys with remaining_secs >= min_remaining"),
    max_remaining: Optional[int] = Query(None, description="Filter keys with remaining_secs <= max_remaining")
):
    return await api_key_service.list_keys(disabled, min_remaining, max_remaining)

@router.post("/create")
async def create_key(api_key_service = Depends(get_api_key_service)):
    return await api_key_service.create_key()
    
@router.patch("/disable/{api_key}")
async def disable_api_key(api_key: str, api_key_service = Depends(get_api_key_service)):
    return await api_key_service.disable_api_key(api_key)