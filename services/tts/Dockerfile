# STAGE 1
# FROM pytorch/pytorch:2.9.1-cuda12.6-cudnn9-runtime AS build
FROM python:3.12-slim AS build

WORKDIR /app

RUN apt-get update && apt-get install -y \
        build-essential libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml ./
RUN pip install --no-cache-dir .
RUN python -m piper.download_voices en_US-lessac-medium --data-dir /voices

COPY tts/ ./tts

# STAGE 2
# FROM pytorch/pytorch:2.9.1-cuda12.6-cudnn9-runtime
FROM python:3.12-slim

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=build /voices app/voices
COPY --from=build /app/tts app/tts

WORKDIR /app

EXPOSE 50052

CMD ["python", "-m", "tts.server"]