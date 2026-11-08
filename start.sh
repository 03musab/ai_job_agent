#!/bin/bash
set -e

# Prevent glibc memory fragmentation in low-memory Linux containers
export MALLOC_ARENA_MAX=2

# Cleanup function to kill background worker if web server exits
cleanup() {
    echo "[start.sh] Web server stopped, terminating background worker..."
    if [ -n "$CELERY_PID" ]; then
        kill -TERM "$CELERY_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

echo "[start.sh] Initializing AI JobSnap..."

# 1. Start Celery worker with single-worker concurrency to fit in 512MB RAM
if [ "${RUN_CELERY_IN_WEB:-true}" = "true" ]; then
    echo "[start.sh] Starting Celery worker (concurrency=1, max-tasks=20)..."
    celery -A app.celery worker --loglevel=info --concurrency=1 --max-tasks-per-child=20 &
    CELERY_PID=$!
    echo "[start.sh] Celery worker running (PID: $CELERY_PID)"
fi

# 2. Start Gunicorn with 1 worker and 4 threads (handles concurrent requests within memory limits)
PORT="${PORT:-5000}"
echo "[start.sh] Starting Gunicorn on 0.0.0.0:$PORT (1 worker, 4 threads)..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 app:app
