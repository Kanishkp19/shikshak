#!/usr/bin/env bash
set -e

PORT="${PORT:-8000}"

echo "=== Starting Shikshak AI Backend ==="
echo "Port: ${PORT}"

# If REDIS_URL is provided and reachable, launch Celery worker in background with concurrency 1
if [ -n "$REDIS_URL" ]; then
    echo "Redis configured. Launching Celery background worker (concurrency=1)..."
    celery -A celery_app worker --loglevel=info --concurrency=1 &
else
    echo "REDIS_URL not set. Running in direct synchronous/FastAPI fallback mode."
fi

# Start FastAPI server in foreground (main process for Render health checks)
echo "Starting Uvicorn web server..."
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
