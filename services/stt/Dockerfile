FROM python:3.12-slim AS build

WORKDIR /app

RUN apt-get update && apt-get install -y \
        build-essential \
        libsndfile1 \
        ffmpeg \
        curl git wget golang \
    && rm -rf /var/lib/apt/lists/*

RUN go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest
RUN cp $(go env GOPATH)/bin/grpcurl /usr/local/bin/grpcurl

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY stt/ ./stt

RUN pip install --no-cache-dir torch==2.9.1+cpu --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir grpcio==1.76.0 grpcio-tools==1.76.0 transformers==4.57.3 accelerate==1.12.0

FROM python:3.12-slim

COPY --from=build /opt/venv /opt/venv
COPY --from=build /usr/local/bin/grpcurl /usr/local/bin/grpcurl

ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /app/stt app/stt

WORKDIR /app

CMD ["python", "-u", "-m", "stt.server"]