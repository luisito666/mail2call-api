from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CallLogBase(BaseModel):
    email_event_id: str
    contact_id: str
    phone_number: str
    call_sid: Optional[str] = None
    status: str
    duration: Optional[int] = None
    attempt_number: Optional[int] = 1
    error_message: Optional[str] = None


class CallLogCreate(CallLogBase):
    pass


class CallLogUpdate(BaseModel):
    email_event_id: Optional[str] = None
    contact_id: Optional[str] = None
    phone_number: Optional[str] = None
    call_sid: Optional[str] = None
    status: Optional[str] = None
    duration: Optional[int] = None
    attempt_number: Optional[int] = None
    error_message: Optional[str] = None


class CallLogResponse(CallLogBase):
    id: int
    created_at: datetime
    updated_at: datetime