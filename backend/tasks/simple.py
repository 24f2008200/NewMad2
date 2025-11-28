# backend/tasks/simple.py
from backend.celery_utils import celery

@celery.task(name="simple.ping")
def ping_task(x):
    print("PING TASK EXECUTED with:", x)
    return {"message": f"pong {x}"}
@celery.task(name="simple.add")
def add(x, y):
    return x + y