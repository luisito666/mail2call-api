from pydantic import BaseModel
from typing import Optional, List, Generic, TypeVar
from datetime import datetime


class TriggerBase(BaseModel):
    name: str
    trigger_string: str
    description: Optional[str] = None
    group_id: Optional[str] = None
    is_active: Optional[bool] = True
    priority: Optional[int] = 1
    custom_message: Optional[str] = None


class TriggerCreate(TriggerBase):
    id: str


class TriggerUpdate(BaseModel):
    name: Optional[str] = None
    trigger_string: Optional[str] = None
    description: Optional[str] = None
    group_id: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    custom_message: Optional[str] = None


class TriggerResponse(TriggerBase):
    id: str
    created_at: datetime
    updated_at: datetime


T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int