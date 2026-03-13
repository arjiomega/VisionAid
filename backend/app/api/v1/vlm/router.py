from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.vlm.dependencies import authenticate_websocket
from app.api.v1.vlm.service import VLMWebSocketService
from app.db.session import get_db
from app.core.logger import logger

router = APIRouter(prefix="/vlm")


@router.websocket("/ws/transcribe-vision-tts")
async def audio_websocket(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db)
):

    current_key = await authenticate_websocket(websocket, db)

    if not current_key:
        return

    vlm_websocket_service = VLMWebSocketService(current_key, websocket, db)

    await websocket.accept()
    logger.info(f"WebSocket connected for '{current_key.id}'.")

    try:
        while True:
            result = await vlm_websocket_service.process_message()

            if not result.continue_loop:
                logger.info("Client disconnected")
                return

    except WebSocketDisconnect:
        logger.warning("WebSocket disconnected unexpectedly.")
    except Exception as e:
        logger.error(f"Error: {e}")
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        await websocket.close()
        logger.info("WebSocket connection closed.")