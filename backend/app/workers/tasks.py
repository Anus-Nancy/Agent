from app.db.session import SessionLocal
from app.services.escalation import escalate_complaints
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.escalate_complaints_task")
def escalate_complaints_task() -> int:
    db = SessionLocal()
    try:
        return escalate_complaints(db)
    finally:
        db.close()
