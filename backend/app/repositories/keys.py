import hashlib
import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update

from app.models.keys import APIKeyDB
from app.core.logger import logger

def generate_api_key(prefix: str = "sk_", length_bytes: int = 32) -> str:
    random_part = secrets.token_hex(length_bytes)  # hex string
    return f"{prefix}{random_part}"

class APIKeyRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def increment_usage(self, key_id: int) -> APIKeyDB:

        # Prevent race condition
        statement = (
            update(APIKeyDB)
            .where(
                APIKeyDB.id == key_id,
                APIKeyDB.disabled == False,
                APIKeyDB.total_requests < APIKeyDB.max_requests
            )
            .values(
                total_requests=APIKeyDB.total_requests + 1,
                disabled=(APIKeyDB.total_requests + 1) >= APIKeyDB.max_requests
            )
            .returning(APIKeyDB)
        )

        result = await self.db.execute(statement)
        updated_key = result.scalar_one_or_none()

        if updated_key is None:
            logger.warning(f"Key '{key_id}' cannot be updated.")
            await self.db.rollback()
            return None
        
        await self.db.commit()

        return updated_key
    
    async def get_by_fingerprint(self, fingerprint: str) -> APIKeyDB | None:
        result = await self.db.execute(
            select(APIKeyDB).where(APIKeyDB.key_fingerprint == fingerprint)
        )
        return result.scalar_one_or_none()
    
    async def get_by_api_key(self, api_key: str) -> APIKeyDB | None:
        fingerprint = hashlib.sha256(api_key.encode()).hexdigest()
        return await self.get_by_fingerprint(fingerprint)

    async def add_key(self, hashed_api_key: str, fingerprint: str, disabled=False, max_requests=5):
        key = APIKeyDB(
            hashed_api_key=hashed_api_key,
            key_fingerprint=fingerprint,
            disabled=disabled,
            max_requests=max_requests
        )
        
        self.db.add(key)

        try:
            await self.db.commit()
            await self.db.refresh(key)
            return key
        except IntegrityError:
            await self.db.rollback()
            return None

    async def disable_key_by_fingerprint(self, fingerprint: str):
  
        statement = (
            update(APIKeyDB)
            .where(
                APIKeyDB.key_fingerprint == fingerprint
            )
            .values(
                disabled=True
            )
            .returning(APIKeyDB)
        )

        result = await self.db.execute(statement)
        updated_key = result.scalar_one_or_none()

        if updated_key:
            await self.db.commit()
            await self.db.refresh(updated_key)
        else:
            await self.db.rollback()
            return {"detail": "Failed to disable API key."}

        return {"detail": "API key disabled successfully."}
    
    async def list_keys(self, disabled=None, min_remaining=None, max_remaining=None):
        query = select(APIKeyDB)
        if disabled is not None:
            query = query.where(APIKeyDB.disabled == disabled)
        if min_remaining is not None:
            query = query.where(APIKeyDB.remaining_secs >= min_remaining)
        if max_remaining is not None:
            query = query.where(APIKeyDB.remaining_secs <= max_remaining)
        result = await self.db.execute(query)
        return result.scalars().all()