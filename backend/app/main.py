import os

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.api.v1.router import router as v1_router

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="VisionAid Whisper API")

cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}