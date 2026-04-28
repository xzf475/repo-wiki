#!/bin/sh
set -e

API_PORT="${API_PORT:-7654}"

if [ "${MCP_ENABLED}" = "true" ]; then
    MCP_PORT="${MCP_PORT:-8000}"
    echo "Starting MCP server on port ${MCP_PORT}..."
    repo-wiki serve --transport streamable-http --port "${MCP_PORT}" --api "http://localhost:${API_PORT}" &
    MCP_PID=$!
    echo "MCP server started (PID: ${MCP_PID})"
fi

echo "Starting REST API server on port ${API_PORT}..."
exec repo-wiki serve-api --host 0.0.0.0 --port "${API_PORT}"
