import time
from typing import Any, Callable, Awaitable, Tuple

from fastapi import WebSocket

from app.services import stt_service, vlm_service, tts_service
from app.core.logger import logger

async def async_fn_timer(
    function: Callable[..., Awaitable[Any]],
    *args,
    **kwargs
) -> Tuple[Any, float]:

    start = time.perf_counter()

    try:
        result = await function(*args, **kwargs)
    except Exception:
        logger.exception(f"Function {function.__name__} failed")
        raise
    finally:
        end = time.perf_counter()

    return result, end - start

class AudioPipeline:

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def send_status(self, status: str):
        await self.websocket.send_json({
            "type": "status",
            "status": status
        })

    async def _transcribe(self, audio_bytes: bytes) -> str:
  
        await self.send_status("transcribing")

        transcription, elapsed = await async_fn_timer(
            stt_service.transcribe_audio,
            audio_bytes
        )

        await self.websocket.send_json({
            "type": "transcription",
            "text": transcription,
            "time": elapsed
        })

        return transcription

    async def _gen_response(self, transcription: str, image_bytes: bytes) -> str:
        
        await self.send_status("thinking")

        response, elapsed = await async_fn_timer(
            vlm_service.generate_caption,
            transcription,
            image_bytes
        )

        await self.websocket.send_json({
            "type": "assistantResponse",
            "text": response,
            "time": elapsed
        })

        return response

    async def _synthesize(self, response: str):

        await self.send_status("synthesizing")

        audio_bytes, _ = await async_fn_timer(
            tts_service.synthesize_text,
            response
        )

        await self.websocket.send_bytes(audio_bytes)

    async def process(self, audio_bytes: bytes, image_bytes: bytes):

        try:
            transcription = await self._transcribe(audio_bytes)
            response = await self._gen_response(transcription, image_bytes)
            await self._synthesize(response)

            await self.websocket.send_json({
                "type": "status",
                "status": "finished"
            })

        except Exception as e:
            logger.exception("Audio pipeline error")

            await self.websocket.send_json({
                "type": "error",
                "message": str(e)
            })