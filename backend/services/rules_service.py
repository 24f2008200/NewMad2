from flask import Blueprint, request, jsonify
from backend.models import ReminderRule, User, db, Reservation
from datetime import datetime, timezone, timedelta  

def execute_rule(rule_id):
    
    from backend.models import User, ParkingLot, ReminderJob, ReminderRule
    from datetime import datetime, timezone
    print(f"Admin requested run of rule ID {rule_id}")
    rule = ReminderRule.query.get(rule_id)
    if not rule:
        return jsonify({"error": "Rule not found"}), 404

    if not rule.active:
        return jsonify({"error": "Rule is inactive"}), 400

    #  STEP 1 — Get candidate users depending on trigger_type
    trigger = rule.trigger_type
    candidates = []
    query = User.query.filter(User.receive_reminders == True)
    if trigger == "not_seen_in_hours":
        hours = int(rule.param_value or 24)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        candidates = query.filter(User.last_seen < cutoff).all()

    elif trigger == "new_parking_lot":
        # All users except admins
        candidates = query.filter(User.role == "user").all()
    elif trigger == "stay_exceeding_hours":
        hours = int(rule.param_value or 2)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        candidates = (
            query.join(Reservation)
            .filter(Reservation.checkin_time < cutoff, Reservation.checkout_time == None)
            .all()
        )
    elif trigger == "broadcast":
        candidates = query.all() 

    else:
        return jsonify({"error": f"Unknown trigger_type '{trigger}'"}), 400

    #  STEP 2 — Insert ReminderJobs for those users
    created = 0
    for user in candidates:
        job = ReminderJob(
            user_id=user.id,
            scheduled_at=datetime.now(timezone.utc),
            status="pending",
            message=rule.message_template,
            action=rule.action
        )
        db.session.add(job)
        created += 1

    db.session.commit()
    rule.last_run_at = datetime.now(timezone.utc)
    if rule.schedule_type == "one_time":
        rule.next_run_at = None
        rule.active = False
    if rule.schedule_type == "daily":
        rule.next_run_at = rule.last_run_at + timedelta(days=1)
    if rule.schedule_type == "hourly":
        rule.next_run_at = rule.last_run_at + timedelta(hours=1)
    if rule.schedule_type == "weekly":
        rule.next_run_at = rule.last_run_at + timedelta(weeks=1)
    if rule.schedule_type == "monthly":
        rule.next_run_at = rule.last_run_at + timedelta(days=30)
    db.session.commit()
    

    return jsonify({
        "status": "ok",
        "rule_id": rule_id,
        "trigger_type": rule.trigger_type,
        "jobs_created": created
    })