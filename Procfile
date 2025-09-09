web: python -m flask run --host=0.0.0.0
worker: celery -A app.celery worker --loglevel=info --pool=solo
beat: celery -A app.celery beat --loglevel=info