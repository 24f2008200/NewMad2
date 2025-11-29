from flask import Blueprint, request, jsonify
from backend.models import ReminderRule, db, Reservation
from datetime import datetime, timezone, timedelta  
from backend.services.rules_service import execute_rule

rules_bp = Blueprint("admin_rules", __name__, url_prefix="/api/admin/rules")

@rules_bp.post("/reminder/<int:rule_id>/run")
def run_rule_now(rule_id):
    """
    Run a reminder rule immediately — used by Admin UI "Run Now" button.
    This does NOT send notifications; it only creates ReminderJob rows
    exactly like your midnight scheduler.
    """
    return execute_rule(rule_id)


@rules_bp.get("/reminder")
def list_rules():
    return jsonify({
        "rules": [
            {
                "id": r.id,
                "rule_name": r.rule_name,
                "trigger_type": r.trigger_type,
                "message_template": r.message_template,
                "schedule_type": r.schedule_type,
                "time_of_day": r.time_of_day,
                "active": r.active,
            }
            for r in ReminderRule.query.all()
        ]
    })


@rules_bp.post("/reminder")
def create_rule():
    data = request.json
    print("Creating rule with data:", data)

    rule = ReminderRule(
        rule_name=data["rule_name"],
        trigger_type=data["trigger_type"],
        action=data["action"],
        message_template=data["message_template"],
        schedule_type=data["schedule_type"],
        time_of_day=data.get("time_of_day", None),
        active=True
    )
 
    db.session.add(rule)
    db.session.commit()
    return jsonify({"status": "created", "id": rule.id})

@rules_bp.put("/reminder/<int:rule_id>")
def update_rule(rule_id):
    data = request.json
    rule = ReminderRule.query.get(rule_id)

    if not rule:
        return jsonify({"error": "Rule not found"}), 404

    # Update allowed fields only
    if "trigger_type" in data:
        rule.trigger_type = data["trigger_type"]

    if "message_template" in data:
        rule.message_template = data["message_template"]

    if "schedule_type" in data:
        rule.schedule_type = data["schedule_type"]

    if "time_of_day" in data:
        rule.time_of_day = data["time_of_day"]

    if "active" in data:
        rule.active = bool(data["active"])

    db.session.commit()

    return jsonify({"status": "updated", "id": rule.id})


@rules_bp.delete("/reminder/<int:rule_id>")
def delete_rule(rule_id):
    rule = ReminderRule.query.get(rule_id)

    if not rule:
        return jsonify({"error": "Rule not found"}), 404

    db.session.delete(rule)
    db.session.commit()

    return jsonify({"status": "deleted", "id": rule_id})
