web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 "app:app"
worker: celery -A app.celery worker --loglevel=info
beat: celery -A app.celery beat --loglevel=info
