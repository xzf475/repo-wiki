# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder

WORKDIR /build

COPY pyproject.toml .
COPY indexer/ indexer/

RUN pip install --no-cache-dir build \
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

EXPOSE 7654

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7654/health')" || exit 1

ENTRYPOINT ["repo-wiki"]
CMD ["serve-api", "--host", "0.0.0.0", "--port", "7654"]
