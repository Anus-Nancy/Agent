from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.complaint import Complaint, ComplaintStatus
from app.models.complaint_history import ComplaintHistory
from app.models.user import User, UserRole
from app.schemas.complaint import ComplaintCreate, ComplaintResponse, ComplaintStatusUpdate
from app.services.classification import classify_department

router = APIRouter(prefix="/complaints", tags=["complaints"])


@router.post("", response_model=ComplaintResponse)
def create_complaint(
    payload: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can submit complaints")

    department = classify_department(db, payload.description)
    if not department:
        raise HTTPException(status_code=500, detail="Department mapping not available")
    complaint = Complaint(
        title=payload.title,
        description=payload.description,
        student_id=current_user.id,
        department_id=department.id,
        status=ComplaintStatus.IN_PROGRESS,
    )
    db.add(complaint)
    db.flush()
    db.add(
        ComplaintHistory(
            complaint_id=complaint.id,
            event_type="Created",
            message=f"Complaint created and routed to {department.name}",
        )
    )
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("", response_model=list[ComplaintResponse])
def list_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Complaint)
    if current_user.role == UserRole.STUDENT:
        query = query.filter(Complaint.student_id == current_user.id)
    return query.order_by(Complaint.created_at.desc()).all()


@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if current_user.role == UserRole.STUDENT and complaint.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return complaint


@router.put("/{complaint_id}/status", response_model=ComplaintResponse)
def update_complaint_status(
    complaint_id: int,
    payload: ComplaintStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in [
        UserRole.STAFF,
        UserRole.ADMIN,
        UserRole.SENIOR_OFFICER,
        UserRole.DEPARTMENT_HEAD,
    ]:
        raise HTTPException(status_code=403, detail="Forbidden")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.status = payload.status
    db.add(
        ComplaintHistory(
            complaint_id=complaint.id,
            event_type="Status Updated",
            message=f"Status changed to {payload.status.value} by user {current_user.id}",
        )
    )
    db.commit()
    db.refresh(complaint)
    return complaint
