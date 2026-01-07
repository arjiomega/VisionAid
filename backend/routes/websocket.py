import json
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from logger import logger
from services import vlm_service, stt_service, tts_service

router = APIRouter()

@router.websocket("/ws/transcribe-vision-tts")
async def audio_websocket(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection accepted for audio processing.")

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
                        print("Received 'done' signal. Processing audio.")

                        # TRANSCRIBE
                        start = time.perf_counter()                        
                        # transcription = await grpc_transcribe(audio_buffer)
                        transcription = await stt_service.transcribe_audio(audio_buffer)
                        end = time.perf_counter()
                        logger.info(f"Transcription: {transcription}")
                        logger.info(f"Transcribe Time: {end-start:.2f} seconds")

                        await websocket.send_text(f"Transcription: {transcription}")

                        # VLM PROCESSING
                        vlm_output = vlm_service.generate_caption(transcription, current_img_bytes)                        

                        # TEXT TO SPEECH
                        start = time.perf_counter()
                        # audio_bytes = await grpc_tts(vlm_output)
                        audio_bytes = await tts_service.synthesize_text(vlm_output)
                        end = time.perf_counter()
                        logger.info(f"TTS Time: {end-start:.2f} seconds")
 
                        await websocket.send_text(f"VLM Caption: {vlm_output}")
                        await websocket.send_bytes(audio_bytes)
                        print("Audio Sent!")
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
                        await websocket.send_text(f"Received chunk of size {len(data)} bytes.")

                    elif data_type == "image":
                        current_img_bytes = data
                        await websocket.send_text(f"Received Image.")
                    else:
                        print("Received invalid data type.")

            elif message["type"] == "websocket.disconnect":
                print("Client disconnected.")
                return

    except WebSocketDisconnect:
        print("WebSocket disconnected unexpectedly.")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        await websocket.close()
        print("WebSocket connection closed.")