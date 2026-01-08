# STAGE 1
FROM python:3.12-slim AS build

WORKDIR /app

RUN apt-get update && apt-get install -y \
        build-essential libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml main.py logger.py ./
COPY clients/ ./clients
COPY generated/ ./generated
COPY routes/ ./routes
COPY services/ ./services

RUN pip install --no-cache-dir .

# STAGE 2
FROM python:3.12-slim

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=build /app/main.py /app/main.py
COPY --from=build /app/logger.py /app/logger.py
COPY --from=build /app/clients app/clients
COPY --from=build /app/generated app/generated
COPY --from=build /app/routes app/routes
COPY --from=build /app/services app/services


WORKDIR /app

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${BACKEND_PORT:-8000}"]