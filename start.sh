#!/bin/bash
set -e

echo "[start.sh] Initializing AI JobSnap..."

# Start Celery background worker if enabled (enabled by default for single-service deployments)
if [ "${RUN_CELERY_IN_WEB:-true}" = "true" ]; then
    echo "[start.sh] Starting Celery worker in background..."
    celery -A app.celery worker --loglevel=info &
    CELERY_PID=$!
    echo "[start.sh] Celery worker running (PID: $CELERY_PID)"

    echo "[start.sh] Starting Celery beat scheduler in background..."
    celery -A app.celery beat --loglevel=info &
    BEAT_PID=$!
    echo "[start.sh] Celery beat running (PID: $BEAT_PID)"
fi

# Start Gunicorn WSGI server in the foreground
PORT="${PORT:-5000}"
echo "[start.sh] Starting Gunicorn on 0.0.0.0:$PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 app:app

