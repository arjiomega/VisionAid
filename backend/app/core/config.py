import os

from dotenv import load_dotenv
load_dotenv()

API_KEY_NAME = "X-API-Key"
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

STT_HOST = os.environ.get("STT_GRPC_HOST")
STT_PORT = os.environ.get("STT_GRPC_PORT")
TTS_HOST = os.environ.get("TTS_GRPC_HOST")
TTS_PORT = os.environ.get("TTS_GRPC_PORT")