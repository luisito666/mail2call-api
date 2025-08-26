from pydantic import BaseModel
from typing import Optional, List, Generic, TypeVar
from datetime import datetime


class ContactGroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True
    emergency_level: Optional[str] = 'medium'


class ContactGroupCreate(ContactGroupBase):
    id: str


class ContactGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    emergency_level: Optional[str] = None


class ContactGroupResponse(ContactGroupBase):
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