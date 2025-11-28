from backend.celery import celery

@celery.task
def test_add(x, y):
    print("Task running...", x, y)
    return x + y
    