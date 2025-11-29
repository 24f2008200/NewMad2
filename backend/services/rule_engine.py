from backend.models import ReminderRule, ReminderJob, db
from datetime import datetime, time
from backend.services.rules_service import execute_rule
from backend.services.triggers import evaluate_trigger

def process_due_rules():
    """Called by your CELERY every hour."""
    now_utc = datetime.utcnow()
    rules = ReminderRule.query.filter_by(active=True).all()
    print(f"Processing {len(rules)} active rules at {now_utc.isoformat()}")
    for rule in rules:
        if rule.next_run_at and rule.next_run_at <= now_utc:
            return execute_rule(rule.id)



def run_all_rules():
    """Called by your CELERY midnight schedule."""
    rules = ReminderRule.query.filter_by(active=True).all()

    for rule in rules:
        print(f"Running rule: {rule.id} ({rule.trigger_type})")
        run_single_rule(rule)


def run_single_rule(rule: ReminderRule):
    """Executes a single rule and generates ReminderJob entries."""

    # Runs logic that returns matching user IDs
    matching_users = evaluate_trigger(rule.trigger_type, rule.params)

    # Time-of-day scheduling (user-defined)
    when = None
    if rule.time_of_day:
        hour, minute = map(int, rule.time_of_day.split(":"))
        when = datetime.combine(datetime.utcnow().date(), time(hour, minute))
    else:
        when = datetime.utcnow()

    for user_id in matching_users:
        job = ReminderJob(
            user_id=user_id,
            scheduled_at=when,
            status="pending",
        )
        db.session.add(job)

    db.session.commit()
    print(f"Rule {rule.id}: Created {len(matching_users)} reminder jobs.")
