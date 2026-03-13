import json

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from fastapi import WebSocket

from app.api.v1.vlm.audio_pipeline import AudioPipeline
from app.models.keys import APIKeyDB
from app.repositories.keys import APIKeyRepository
from app.api.v1.vlm.dependencies import InputBuffer
from app.core.logger import logger


class WebSocketMessage(BaseModel):
    type: str | None
    content: str | bytes | None

    def is_disconnect(self) -> bool:
        return self.type == "websocket.disconnect"

    def is_text(self) -> bool:
        return self.type == "text"

    def is_bytes(self) -> bool:
        return self.type == "bytes"

    def is_ready_to_start_pipeline(self) -> bool:
        return self.content == "done"

class ShouldContinue(BaseModel):
    continue_loop: bool

class VLMWebSocketService:

    def __init__(
            self, 
            key: APIKeyDB,
            websocket: WebSocket, 
            db: AsyncSession, 
    ):
        self.key = key
        self.websocket = websocket
        self.repo = APIKeyRepository(db)
        self.audio_pipeline = AudioPipeline(websocket)
        self.buffer = InputBuffer()

    def _parse_message(self, message: dict) -> WebSocketMessage:

        if "text" in message and message["text"] is not None:
            return WebSocketMessage(type="text", content=message["text"])

        if "bytes" in message and message["bytes"] is not None:
            return WebSocketMessage(type="bytes", content=message["bytes"])

        return WebSocketMessage(type=None, content=None)

    async def process_message(self) -> ShouldContinue:
        message = await self.websocket.receive()
        websocket_message = self._parse_message(message)

        if websocket_message.is_disconnect():
            return ShouldContinue(continue_loop=False)
        
        if websocket_message.is_text():
            if websocket_message.is_ready_to_start_pipeline():
                try:
                    await self.audio_pipeline.process(self.buffer.audio, self.buffer.image)
                except Exception:
                    logger.exception(f"Audio Pipeline failed.")
                finally:
                    await self.repo.increment_usage(self.key.id)
                    logger.info(f"ID: {self.key.id} has used {self.key.total_requests} / {self.key.max_requests}")
                    self.buffer.reset()
            else:
                try:
                    metadata = json.loads(websocket_message.content)
                    self.buffer.set_type(metadata)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to load json: {e}")

        elif websocket_message.is_bytes():
            self.buffer.add_bytes(websocket_message.content)

        return ShouldContinue(continue_loop=True)