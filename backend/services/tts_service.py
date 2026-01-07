import os
import asyncio

from clients.tts_client import TTSClient
from services.utils import executor

tts_host = os.environ.get("TTS_GRPC_HOST")
tts_port = os.environ.get("TTS_GRPC_PORT")

tts_client = TTSClient(tts_host, tts_port)

async def synthesize_text(text: str) -> bytes:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        lambda: tts_client.synthesize(text)
    )
