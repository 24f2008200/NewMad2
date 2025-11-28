from flask import Blueprint, jsonify, request
from celery.result import AsyncResult
from backend.celery_utils  import celery

bp = Blueprint("task_actions", __name__)


# ------------------------------------------------------------
# CANCEL (REVOKE) a Celery task
# ------------------------------------------------------------
@bp.post("/tasks/<task_id>/cancel")
def cancel_task(task_id):
    try:
        celery.control.revoke(task_id, terminate=True)
        return jsonify({"status": "ok", "message": f"Task {task_id} cancelled"}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


# ------------------------------------------------------------
# RUN TASK manually
# ------------------------------------------------------------
@bp.post("/tasks/run")
def run_task():
    data = request.get_json() or {}
    task_name = data.get("task")
    args = data.get("args", [])
    kwargs = data.get("kwargs", {})

    if not task_name:
        return {"error": "task is required"}, 400

    try:
        task = celery.send_task(task_name, args=args, kwargs=kwargs)
        return {"status": "started", "task_id": task.id}
    except Exception as e:
        return {"error": str(e)}, 500
