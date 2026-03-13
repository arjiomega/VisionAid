from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import jwt

from app.repositories.keys import APIKeyRepository
from app.api.v1.auth.schema import Token
from app.core import config


access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)
    expire += (expires_delta if expires_delta else timedelta(minutes=15))
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = APIKeyRepository(db)

    async def authenticate_api_key(self, api_key: str):

        key = await self.repo.get_by_api_key(api_key)

        if not key:
            raise HTTPException(
                status_code=401, 
                detail="API key doesn't exist.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if key.disabled or key.total_requests >= key.max_requests:
            raise HTTPException(
                status_code=401, 
                detail="Expired API key.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "api_key_id": str(key.id),
                "key_fingerprint": key.key_fingerprint,
                "hashed_api_key": key.hashed_api_key
            }, 
            expires_delta=access_token_expires
        )

        return Token(access_token=access_token, token_type="bearer")