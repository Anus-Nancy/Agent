from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "tcf_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    timezone="UTC",
    task_track_started=True,
)

celery_app.conf.beat_schedule = {
    "escalate-complaints-every-10-min": {
        "task": "app.workers.tasks.escalate_complaints_task",
        "schedule": settings.escalation_check_interval_minutes * 60,
    }
}

celery_app.autodiscover_tasks(["app.workers"])
