import os
import asyncio

from clients.stt_client import STTClient
from services.utils import executor

stt_host = os.environ.get("STT_GRPC_HOST")
stt_port = os.environ.get("STT_GRPC_PORT")

stt_client = STTClient(stt_host, stt_port)

async def transcribe_audio(audio: bytes) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        lambda: stt_client.transcribe(audio)
    )
