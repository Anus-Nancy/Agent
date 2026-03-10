from datetime import datetime

from pydantic import BaseModel

from app.models.complaint import ComplaintStatus


class ComplaintCreate(BaseModel):
    title: str
    description: str


class ComplaintStatusUpdate(BaseModel):
    status: ComplaintStatus


class ComplaintResponse(BaseModel):
    id: int
    title: str
    description: str
    status: ComplaintStatus
    department_id: int
    escalation_level: int
    created_at: datetime

    class Config:
        from_attributes = True
