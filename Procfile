web: python -m flask run --host=0.0.0.0 --debug --reload
worker: python -m celery -A app.celery worker --loglevel=info --pool=solo
beat: python -m celery -A app.celery beat --loglevel=info