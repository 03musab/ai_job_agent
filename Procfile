web: python app.py
worker: celery -A app.celery worker --loglevel=info -P gevent
beat: celery -A app.celery beat --loglevel=info