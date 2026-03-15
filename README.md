# VisionAid
Assist vision impaired individuals with AI

## Setup

### Docker Compose

**Required Environment Variables**

| Variable            | Description                                   |
| ------------------- | --------------------------------------------- |
| `POSTGRES_USER`     | PostgreSQL username                           |
| `POSTGRES_PASSWORD` | PostgreSQL password                           |
| `POSTGRES_DB`       | Name of the PostgreSQL database               |
| `OPENAI_API_KEY`    | API key for OpenAI backend integration        |
| `SECRET_KEY`        | Secret key used by FastAPI for signing tokens |


**Optional or Default Variables**
| Variable                | Default           | Explanation                |
| ----------------------- | ----------------- | -------------------------- |
| `POSTGRES_PORT`         | `5432`            | Database port              |
| `TTS_GRPC_HOST`         | `tts-grpc`        | gRPC TTS service hostname  |
| `TTS_GRPC_PORT`         | `50051`           | gRPC TTS service port      |
| `STT_GRPC_HOST`         | `stt-grpc`        | gRPC STT service hostname  |
| `STT_GRPC_PORT`         | `50051`           | gRPC STT service port      |
| `BACKEND_PORT`          | `8000`            | Exposed backend HTTP port  |
| Various `NEXT_PUBLIC_*` | Frontend defaults | Used by the frontend build |
| `CORS_ORIGINS` | `*` | Comma-separated list of allowed frontend origins |


1. Create .env file with the following variables
```env
###########################################################
# PostgreSQL (Database)
###########################################################
POSTGRES_USER=admin
POSTGRES_PASSWORD=supersecret
POSTGRES_DB=visualaid_db
POSTGRES_PORT=5432

###########################################################
# Backend Application
###########################################################
# Required: OpenAI API key for the backend
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# Required: Secret key for signing tokens
SECRET_KEY=your_secret_key_here

# Optional: Number of minutes to expire access tokens
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional: GRPC services (defaults work for compose setup)
TTS_GRPC_HOST=tts-grpc
TTS_GRPC_PORT=50051
STT_GRPC_HOST=stt-grpc
STT_GRPC_PORT=50051

# Optional: Backend exposed port
BACKEND_PORT=8000

# Optional: Allowed origins for CORS (comma-separated)
# Example: http://localhost:3000,http://192.168.1.5:3000
CORS_ORIGINS=http://localhost:3000

###########################################################
# Frontend (Next.js)
###########################################################
NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8000
NEXT_PUBLIC_BACKEND_BASE_WS_URL=ws://localhost:8000
NEXT_PUBLIC_VLM_WS_ENDPOINT=/v1/vlm/ws/transcribe-vision-tts
NEXT_PUBLIC_HEALTHCHECK_ENDPOINT=/health
NEXT_PUBLIC_AUTH_ENDPOINT=/v1/auth/token
```


2. Run
```bash
docker compose up --build -d

# OR exclude frontend
docker compose --profile backend up --build -d
```

3. Clean up
```bash
docker compose down

# OR if frontend excluded
docker compose --profile backend down
```