# VisionAID Backend

```bash
docker build -t visionaid-backend .
docker run --env-file .env -p 8000:8000 visionaid-backend:latest
```