# backend/celery_app.py

from backend.app import create_app
from backend.celery_utils import celery, init_celery

# Create Flask app
app = create_app()

# Bind Celery to Flask
init_celery(app)

# Export Celery instance for worker
__all__ = ("celery",)
