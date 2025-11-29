# backend/celery_setup.py

from backend.celery_instance import celery



def init_celery(app):
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone=app.config.get("CELERY_TIMEZONE", "Asia/Kolkata"),
        enable_utc=True,

        #  Add Beat Schedule here
        beat_schedule={
            "run-demo-task-every-10-seconds": {
                "task": "tasks.demo_task",
                "schedule": 10.0,
            },
            "run-failing-task-every-20-seconds": {
                "task": "tasks.demo_fail",
                "schedule": 20.0,
            },
            # add more repeating tasks here…
        },
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    celery.autodiscover_tasks(["backend.tasks"])

    import backend.services.celery_signals  # ensure signals are imported
