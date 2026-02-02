from fastapi import FastAPI

from routes.websocket import router as websocket_router

app = FastAPI(title="VisionAid Whisper API")

app.include_router(websocket_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}