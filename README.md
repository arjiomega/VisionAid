# VisionAid
Assist vision impaired individuals with AI

## Setup

### Docker Compose

1. Create .env file with the following variables
```env
OPENAI_API_KEY=
TTS_GRPC_HOST=
TTS_GRPC_PORT=
STT_GRPC_HOST=
STT_GRPC_PORT=
```

2. Run
```bash
docker compose up --build -d
```