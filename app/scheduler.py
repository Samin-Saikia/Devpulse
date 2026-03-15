from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

_scheduler = None


def start_scheduler(app):
    global _scheduler
    if _scheduler and _scheduler.running:
        return

    _scheduler = BackgroundScheduler()

    def sync_all_users():
        with app.app_context():
            from app.models.user import User
            from app.services.sync import sync_user
            users = User.query.all()
            app.logger.info(f"Scheduler: syncing {len(users)} user(s)")
            for user in users:
                try:
                    sync_user(user.id)
                except Exception as e:
                    app.logger.error(f"Scheduler sync error for {user.username}: {e}")

    _scheduler.add_job(
        func=sync_all_users,
        trigger=IntervalTrigger(hours=24),
        id="sync_all_users",
        name="Sync all users every 24 hours",
        replace_existing=True,
    )

    _scheduler.start()
    atexit.register(lambda: _scheduler.shutdown())
    app.logger.info("Background scheduler started")
