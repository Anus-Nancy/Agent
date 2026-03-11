from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.escalation import escalate_complaints

scheduler = AsyncIOScheduler()


def _run_escalation_job() -> None:
    db = SessionLocal()
    try:
        escalate_complaints(db)
    finally:
        db.close()


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.add_job(
            _run_escalation_job,
            "interval",
            minutes=settings.escalation_check_interval_minutes,
            id="complaint-escalation-job",
            replace_existing=True,
        )
        scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()
