from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.complaint import Complaint, ComplaintStatus
from app.models.complaint_history import ComplaintHistory


def escalate_complaints(db: Session) -> int:
    now = datetime.utcnow()
    open_complaints = (
        db.query(Complaint)
        .filter(Complaint.status.in_([ComplaintStatus.SUBMITTED, ComplaintStatus.IN_PROGRESS, ComplaintStatus.ESCALATED]))
        .all()
    )

    escalated_count = 0
    for complaint in open_complaints:
        age = now - complaint.created_at
        if age >= timedelta(hours=24) and complaint.escalation_level < 2:
            complaint.escalation_level = 2
            complaint.status = ComplaintStatus.ESCALATED
            db.add(
                ComplaintHistory(
                    complaint_id=complaint.id,
                    event_type="Escalated",
                    message="Escalated to Department Head after 24 hours unresolved.",
                )
            )
            escalated_count += 1
        elif age >= timedelta(hours=8) and complaint.escalation_level < 1:
            complaint.escalation_level = 1
            complaint.status = ComplaintStatus.ESCALATED
            db.add(
                ComplaintHistory(
                    complaint_id=complaint.id,
                    event_type="Escalated",
                    message="Escalated to Senior Officer after 8 hours unresolved.",
                )
            )
            escalated_count += 1

    if escalated_count:
        db.commit()
    return escalated_count
