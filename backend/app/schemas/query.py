from datetime import datetime

from pydantic import BaseModel


class QueryCreate(BaseModel):
    query_text: str


class QueryResponse(BaseModel):
    id: int
    query_text: str
    answer_text: str | None
    status: str
    department_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True
