import asyncio
import json
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from logger import logger
from services import vlm_service, stt_service, tts_service

router = APIRouter()

@router.websocket("/ws/transcribe-vision-tts")
async def audio_websocket(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted for audio processing.")

    audio_buffer = b""
    current_img_bytes: bytes = None
    data_type = None

    try:
        while True:
     
            message = await websocket.receive()

            if message["type"] == "websocket.receive":

                if message.get("text") is not None:
                    text = message["text"]
                    if text == "done":

                        # TRANSCRIBE
                        await websocket.send_json({
                            "type": "status",
                            "status": "transcribing"
                        })
                        start = time.perf_counter()                        
                        transcription = await stt_service.transcribe_audio(audio_buffer)
                        end = time.perf_counter()
                        logger.info(f"Transcription: {transcription}")
                        logger.info(f"Transcribe Time: {end-start:.2f} seconds")

                        await websocket.send_json({
                            "type": "transcription",
                            "text": transcription,
                            "time": end-start
                        })

                        # VLM PROCESSING
                        await websocket.send_json({
                            "type": "status",
                            "status": "thinking"
                        })
                        
                        start = time.perf_counter() 
                        vlm_output = vlm_service.generate_caption(transcription, current_img_bytes)                        
                        end = time.perf_counter()

                        await websocket.send_json({
                            "type": "assistantResponse",
                            "text": vlm_output,
                            "time": end-start
                        })

                        # TEXT TO SPEECH
                        await websocket.send_json({
                            "type": "status",
                            "status": "synthesizing"
                        })

                        start = time.perf_counter()
                        audio_bytes = await tts_service.synthesize_text(vlm_output)
                        end = time.perf_counter()
                        logger.info(f"TTS Time: {end-start:.2f} seconds")
 
                        await websocket.send_bytes(audio_bytes)
                        break


                    try:
                        metadata = json.loads(text)
                        data_type = metadata.get("data_type")
                        logger.debug("NEW DATA TYPE: ", data_type)
                    except json.JSONDecodeError:
                        pass

                if message.get("bytes") is not None:
                    data = message["bytes"]

                    if data_type == "audio":
                        audio_buffer += data

                    elif data_type == "image":
                        current_img_bytes = data
                    else:
                        logger.warning("Received invalid data type.")

            elif message["type"] == "websocket.disconnect":
                logger.info("Client disconnected.")
                return

    except WebSocketDisconnect:
        logger.warning("WebSocket disconnected unexpectedly.")
    except Exception as e:
        logger.error(f"Error: {e}")
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        await websocket.close()
        logger.info("WebSocket connection closed.")