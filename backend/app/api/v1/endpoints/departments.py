from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.department import Department
from app.schemas.department import DepartmentResponse

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentResponse])
def list_departments(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return db.query(Department).order_by(Department.name.asc()).all()
