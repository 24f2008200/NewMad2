from flask import Blueprint, jsonify
from backend.extensions import redis_conn

bp = Blueprint("tasks_api", __name__)

# Redis keys follow pattern:
#   task:<uuid>:status
#   task:<uuid>:result
#   task:<uuid>:meta

@bp.route("/tasks")
def list_tasks():
    tasks = []

    for key in redis_conn.scan_iter("celery-task-meta-*"):
        tid = key.decode().replace("celery-task-meta-", "")
        meta = redis_conn.get(key)

        try:
            import json
            data = json.loads(meta)
        except:
            data = None

        tasks.append({
            "id": tid,
            "status": data.get("status") if data else "unknown",
            "result": data.get("result") if data else None,
            "traceback": data.get("traceback") if data else None,
            "date_done": data.get("date_done") if data else None,
        })

    return jsonify(tasks)
