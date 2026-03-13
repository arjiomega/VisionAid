import asyncio

from app.clients.stt_client import STTClient
from app.core.logger import logger
from .utils import executor
from app.core import config

if config.STT_HOST is None or config.STT_PORT is None:
    logger.error(f"STT HOST: {config.STT_HOST} | STT PORT: {config.STT_PORT}")
    raise ValueError("STT_HOST or STT_PORT not set")

stt_client = STTClient(config.STT_HOST, config.STT_PORT)

async def transcribe_audio(audio: bytes) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        lambda: stt_client.transcribe(audio)
    )
