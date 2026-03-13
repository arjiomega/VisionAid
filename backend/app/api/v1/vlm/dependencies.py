import jwt

from fastapi import WebSocket, WebSocketException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.keys import APIKeyDB
from app.core.logger import logger
from app.core import config


class InputBuffer:

    def __init__(self):
        self.audio: bytes = b""
        self.image: bytes | None = None
        self.data_type: str | None = None

    def set_type(self, metadata: dict):
        self.data_type = metadata.get("data_type")

    def add_bytes(self, data: bytes):

        if self.data_type == "audio":
            self.audio += data

        elif self.data_type == "image":
            self.image = data

    def reset(self):
        self.audio = b""
        self.image = None
        self.data_type = None

async def get_current_key(access_token: str, db: AsyncSession) -> APIKeyDB:

    credentials_exception = WebSocketException(
        code=status.WS_1008_POLICY_VIOLATION,
        reason="Could not validate credentials",
    )

    try:
        payload = jwt.decode(
            access_token,
            config.SECRET_KEY,
            algorithms=config.ALGORITHM
        )

        logger.debug(f"PAYLOAD: {payload}")

        api_key_id = payload.get("api_key_id")
        hashed_api_key = payload.get("hashed_api_key")
        key_fingerprint = payload.get("key_fingerprint")

        result = await db.execute(
            select(APIKeyDB).where(APIKeyDB.key_fingerprint == key_fingerprint)
        )

        key = result.scalar_one_or_none()

        if not key or key.disabled or key.hashed_api_key != hashed_api_key:
            error_response = f"ID: {api_key_id} "
            if not key:
                logger.error(error_response + "does not exist.")
            if key.disabled:
                logger.error(error_response + "is expired / disabled.")
            if key.hashed_api_key != hashed_api_key:
                logger.error(error_response + "submitted with invalid hashed api_key.")
            raise credentials_exception

        return key

    except jwt.InvalidTokenError as e:
        logger.error(f"JWT Error: {e}")
        raise credentials_exception
    
async def authenticate_websocket(websocket: WebSocket, db: AsyncSession) -> APIKeyDB:
    access_token = websocket.query_params.get("token")

    if not access_token:
        await websocket.close(code=1008 , reason="Invalid access.")
        return
    try:
        current_key = await get_current_key(access_token, db)
    except WebSocketException as e:
        logger.error(f"Authenticating Websocket Failed: {e}")
        await websocket.close(code=1008, reason=e)
        return None

    if current_key.disabled:
        logger.error(f"ID: {current_key.id} is now expired.")
        await websocket.close(code=1008, reason="Expired API Key")
        return None
    
    return current_key