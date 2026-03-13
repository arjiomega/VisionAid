from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from app.api.v1.auth.service import AuthService
from app.db.session import get_db
from app.core import config
from app.api.v1.auth.schema import Token

router = APIRouter(prefix="/auth")

api_key_header = APIKeyHeader(name=config.API_KEY_NAME, auto_error=False)

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

@router.post("/token")
async def login_for_access_token(
    api_key: str = Depends(api_key_header),
    auth_service = Depends(get_auth_service),
) -> Token:
    
    return await auth_service.authenticate_api_key(api_key)