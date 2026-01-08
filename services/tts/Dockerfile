# STAGE 1
FROM python:3.12-slim AS build

WORKDIR /app

RUN apt-get update && apt-get install -y \
        build-essential libsndfile1 \
        curl git wget golang \
    && rm -rf /var/lib/apt/lists/*

RUN go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest
RUN cp $(go env GOPATH)/bin/grpcurl /usr/local/bin/grpcurl

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml ./
COPY tts/ ./tts
RUN pip install --no-cache-dir .
RUN python -m piper.download_voices en_US-lessac-medium --data-dir /voices

# STAGE 2
FROM python:3.12-slim

COPY --from=build /opt/venv /opt/venv
COPY --from=build /usr/local/bin/grpcurl /usr/local/bin/grpcurl

ENV PATH="/opt/venv/bin:$PATH"

COPY --from=build /voices app/voices
COPY --from=build /app/tts app/tts

WORKDIR /app

CMD ["python", "-u", "-m", "tts.server"]