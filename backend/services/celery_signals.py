# backend/services/celery_signals.py
from datetime import datetime
from celery.signals import task_prerun, task_postrun, task_failure, task_revoked
from sqlalchemy.exc import SQLAlchemyError
from backend.models import db, TaskRecord
from flask import current_app

@task_prerun.connect
def on_task_prerun(sender=None, task_id=None, task=None, args=None, kwargs=None, **kw):
    """Called just before task runs — create or update a row."""
    with current_app.app_context():
        try:
            rec = TaskRecord.query.get(task_id)
            now = datetime.utcnow()
            if not rec:
                rec = TaskRecord(
                    id=task_id,
                    name=getattr(task, "name", str(sender)),
                    status="RUNNING",
                    start_time=now,
                    worker=kw.get("hostname") or None,
                    progress=0,
                )
                db.session.add(rec)
            else:
                rec.status = "RUNNING"
                rec.start_time = now
                rec.worker = kw.get("hostname") or rec.worker
                rec.progress = rec.progress or 0
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            # log exception if you have logging configured
        print(f"Task {task_id} started.")
@task_postrun.connect
def on_task_postrun(sender=None, task_id=None, task=None, retval=None, state=None, **kw):
    """Called after task completes (success or failure)."""
    with current_app.app_context():
        try:
            rec = TaskRecord.query.get(task_id)
            now = datetime.utcnow()
            if not rec:
                rec = TaskRecord(id=task_id, name=getattr(task, "name", str(sender)))
                db.session.add(rec)

            # Celery sometimes gives state; fallback to SUCCESS unless failure signal fired
            rec.status = "SUCCESS"
            rec.end_time = now
            if rec.start_time:
                rec.duration = (rec.end_time - rec.start_time).total_seconds()
            else:
                rec.duration = None
            rec.progress = 100
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
        print(f"Task {task_id} completed successfully.")
@task_failure.connect
def on_task_failure(sender=None, task_id=None, exception=None, traceback=None, **kw):
    """Called when task fails with exception."""
    with current_app.app_context():
        try:
            rec = TaskRecord.query.get(task_id)
            now = datetime.utcnow()
            if not rec:
                rec = TaskRecord(id=task_id, name=getattr(sender, "name", str(sender)))
            db.session.add(rec)
            rec.status = "FAILED"
            rec.end_time = now
            if rec.start_time:
                rec.duration = (rec.end_time - rec.start_time).total_seconds()
                rec.progress = rec.progress or 0
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
        print(f"Task {task_id} failed with exception: {exception}")
@task_revoked.connect
def on_task_revoked(request=None, terminated=None, signum=None, expired=None, **kw):
    # note: Celery signature for revoked varies — we try to get id from request
    with current_app.app_context():
        try:
            task_id = getattr(request, "id", None) or kw.get("task_id")
            if not task_id:
                return
            rec = TaskRecord.query.get(task_id)
            now = datetime.utcnow()
            if not rec:
                rec = TaskRecord(id=task_id, name="(revoked)")
                db.session.add(rec)
            rec.status = "REVOKED"
            rec.end_time = now
            if rec.start_time:
                rec.duration = (rec.end_time - rec.start_time).total_seconds()
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
        print(f"Task {task_id} was revoked.")