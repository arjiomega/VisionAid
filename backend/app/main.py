from fastapi import FastAPI

from app.api.v1.router import router as v1_router

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="VisionAid Whisper API")

app.include_router(v1_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}