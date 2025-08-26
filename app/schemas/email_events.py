from pydantic import BaseModel
from typing import Optional, List, Generic, TypeVar
from datetime import datetime


class EmailEventBase(BaseModel):
    from_email: str
    subject: Optional[str] = None
    body: Optional[str] = None
    trigger_matched: Optional[str] = None
    status: Optional[str] = 'pending'


class EmailEventCreate(EmailEventBase):
    id: str


class EmailEventUpdate(BaseModel):
    from_email: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    trigger_matched: Optional[str] = None
    status: Optional[str] = None


class EmailEventResponse(EmailEventBase):
    id: str
    received_at: datetime
    processed_at: Optional[datetime] = None


T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int