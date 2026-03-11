from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.models.query_log import QueryLog
from app.models.user import User, UserRole
from app.schemas.query import QueryCreate, QueryResponse
from app.services.classification import classify_department
from app.services.query_similarity import query_similarity_service

router = APIRouter(prefix="/queries", tags=["queries"])


@router.post("", response_model=QueryResponse)
def create_query(
    payload: QueryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    similar_answer = query_similarity_service.find_similar_answer(
        payload.query_text,
        threshold=settings.query_similarity_threshold,
    )

    if similar_answer:
        query = QueryLog(
            student_id=current_user.id,
            query_text=payload.query_text,
            answer_text=similar_answer,
            status="Answered",
            department_id=None,
        )
        db.add(query)
        db.commit()
        db.refresh(query)
        query_similarity_service.add_answered_query(query.id, query.query_text, query.answer_text or "")
        return query

    department = classify_department(db, payload.query_text)
    query = QueryLog(
        student_id=current_user.id,
        query_text=payload.query_text,
        status="Pending",
        department_id=department.id if department else None,
    )
    db.add(query)
    db.commit()
    db.refresh(query)
    return query


@router.get("", response_model=list[QueryResponse])
def list_queries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(QueryLog)
    if current_user.role == UserRole.STUDENT:
        q = q.filter(QueryLog.student_id == current_user.id)
    return q.order_by(QueryLog.created_at.desc()).all()
