from datetime import datetime, timezone, timedelta
from backend.models import db, ReminderJob, User
from backend.services.mail_utils import send_email
from backend.services.chat_utils import send_chat


def create_daily_reminder_jobs():
    """
    Called once per day at midnight.
    For each user who qualifies, create a ReminderJob entry
    for their chosen reminder time (e.g., 18:00 IST).
    """
    utc_now = datetime.now(timezone.utc)
    today = utc_now.date()

    users = User.query.filter(
        User.active == True
    ).all()

    jobs = []
    for user in users:
        # user.reminder_time is stored in HH:MM format or datetime.time
        reminder_time = user.reminder_time or None
        if not reminder_time:
            continue

        # Build the datetime for tonight
        scheduled_at = datetime(
            today.year, today.month, today.day,
            reminder_time.hour, reminder_time.minute,
            tzinfo=timezone.utc
        )

        job = ReminderJob(
            user_id=user.id,
            scheduled_at=scheduled_at,
            status="pending"
        )
        jobs.append(job)

    if jobs:
        db.session.bulk_save_objects(jobs)
        db.session.commit()

    return len(jobs)



def process_due_reminders():
    """
    Runs every minute.
    Sends notifications for ANY job whose scheduled_at <= now
    and status is pending.
    """
    utc_now = datetime.now(timezone.utc)
    print("Processing due reminders at", utc_now.isoformat())
    due_jobs = ReminderJob.query.filter(
        ReminderJob.status == "pending",
        ReminderJob.scheduled_at <= utc_now
    ).all()
    print(f"Found {len(due_jobs)} due reminder jobs.")
    for job in due_jobs:
        user = User.query.get(job.user_id)
        if not user:
            continue
        if job.action == "send_reminder":
            # send via chat or mail based on user prefs
            if user.google_chat_webhook :
                send_chat(user.google_chat_webhook, job.message)
            else:
                send_email(user.email, "Parking Reminder", job.message)
            print(f"Sent reminder to user {user.id} via {'chat' if user.google_chat_webhook else 'email'}.")
        elif job.action == "other_action":
            # Implement other actions as needed
            pass

        job.status = "sent"
        job.sent_at = utc_now

    if due_jobs:
        db.session.commit()

    return len(due_jobs)
