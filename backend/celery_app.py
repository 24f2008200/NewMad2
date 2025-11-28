# backend/celery_app.py

from backend.celery_instance import celery
from backend.celery_setup import init_celery
from backend.app import create_app

flask_app = create_app()
init_celery(flask_app)

__all__ = ("celery",)
