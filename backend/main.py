from fastapi import FastAPI

from routes.websocket import router as websocket_router

app = FastAPI(title="VisionAid Whisper API")

app.include_router(websocket_router)