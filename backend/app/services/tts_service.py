import os
import asyncio

from app.clients.tts_client import TTSClient
from .utils import executor
from app.core import config
from app.core.logger import logger

if config.TTS_HOST is None or config.TTS_PORT is None:
    logger.error(f"STT HOST: {config.TTS_HOST} | STT PORT: {config.TTS_PORT}")
    raise ValueError("TTS_HOST or TTS_PORT not set")

tts_client = TTSClient(config.TTS_HOST, config.TTS_PORT)

async def synthesize_text(text: str) -> bytes:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        lambda: tts_client.synthesize(text)
    )
