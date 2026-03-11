from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.department import Department
from app.models import complaint, complaint_history, department, knowledge_base, query_log, user  # noqa: F401
from app.workers.scheduler import start_scheduler, stop_scheduler
from app.services.query_similarity import query_similarity_service
from app.services.rag_chatbot import rag_chatbot_service

DEFAULT_DEPARTMENTS = [
    "Fee Department",
    "Scholarship Department",
    "Admissions Department",
    "IT Department",
    "Student Support Department",
]


def seed_departments() -> None:
    db = SessionLocal()
    try:
        existing = {d.name for d in db.query(Department).all()}
        for dept_name in DEFAULT_DEPARTMENTS:
            if dept_name not in existing:
                db.add(Department(name=dept_name))
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_departments()
    db = SessionLocal()
    try:
        query_similarity_service.rebuild_from_database(db)
        rag_chatbot_service.sync_knowledge_base(db)
    finally:
        db.close()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health")
def health_check():
    return {"status": "ok"}
