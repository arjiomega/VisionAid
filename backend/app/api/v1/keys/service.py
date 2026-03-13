import hashlib
import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.repositories.keys import APIKeyRepository
from app.core.security import password_hash

def generate_api_key(prefix: str = "sk_", length_bytes: int = 32) -> str:
    random_part: str = secrets.token_hex(length_bytes)
    return f"{prefix}{random_part}"

class APIKeyService:

    def __init__(self, db: AsyncSession):
        self.repo = APIKeyRepository(db)

    async def list_keys(self, disabled, min_remaining, max_remaining):
        keys = await self.repo.list_keys(disabled, min_remaining, max_remaining)

        # Return safe info
        return [
            {
                "id": key.id,
                "disabled": key.disabled,
                "total_requests": key.total_requests,
                "max_requests": key.max_requests
            }
            for key in keys
        ]

    async def create_key(self):

        for _ in range(5):
            api_key = generate_api_key()
            key_fingerprint = hashlib.sha256(api_key.encode()).hexdigest()
            hashed_api_key = password_hash.hash(api_key)

            try:
                new_key = await self.repo.add_key(
                    hashed_api_key,
                    key_fingerprint
                )
                if new_key:
                    return {
                        "detail": "API Key successfully created",
                        "API Key": api_key
                    }
            except Exception:
                continue

        raise HTTPException(status_code=500, detail="Failed to create API key.")

    async def disable_api_key(self, api_key: str):
        key_fingerprint = hashlib.sha256(api_key.encode()).hexdigest()

        return await self.repo.disable_key_by_fingerprint(key_fingerprint)