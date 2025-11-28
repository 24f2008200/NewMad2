# backend/celery_utils.py

from celery import Celery
from flask import Flask

celery = Celery(__name__)

def init_celery(app: Flask):
    """
    Attach Flask app configuration to Celery.
    Ensures Redis is used instead of AMQP (RabbitMQ).
    """
    # Load all celery-related config from Flask config.py
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        task_serializer=app.config.get("CELERY_TASK_SERIALIZER", "json"),
        result_serializer=app.config.get("CELERY_RESULT_SERIALIZER", "json"),
        accept_content=app.config.get("CELERY_ACCEPT_CONTENT", ["json"]),
        timezone=app.config.get("CELERY_TIMEZONE", "Asia/Kolkata"),
        enable_utc=app.config.get("CELERY_ENABLE_UTC", True),
    )

    # Make Celery tasks run inside Flask application context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    celery.autodiscover_tasks(["backend.tasks"])

    return celery
