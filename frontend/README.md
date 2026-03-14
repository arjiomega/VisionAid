For dev create .env.local

```env
NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8000
NEXT_PUBLIC_BACKEND_BASE_WS_URL=ws://localhost:8000
NEXT_PUBLIC_VLM_WS_ENDPOINT=/v1/vlm/ws/transcribe-vision-tts
NEXT_PUBLIC_HEALTHCHECK_ENDPOINT=/health
NEXT_PUBLIC_AUTH_ENDPOINT=/v1/auth/token
```