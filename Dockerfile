# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder

WORKDIR /build

COPY pyproject.toml .
COPY indexer/ indexer/

RUN pip install --no-cache-dir build setuptools wheel \
    && python -m build --wheel --no-isolation

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl \
    && rm /tmp/*.whl

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 7654 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"API_PORT\",\"7654\")}/health')" || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
