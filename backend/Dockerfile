# STAGE 1
FROM python:3.12-slim AS build

WORKDIR /app

RUN apt-get update && apt-get install -y \
        build-essential libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml ./
COPY app/ ./app
COPY generated/ ./generated

RUN pip install --no-cache-dir .

# STAGE 2
FROM python:3.12-slim

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=build /app /app

WORKDIR /app

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]