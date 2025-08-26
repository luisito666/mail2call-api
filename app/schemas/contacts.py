from pydantic import BaseModel
from typing import Optional, List, Generic, TypeVar
from datetime import datetime


class ContactBase(BaseModel):
    name: str
    phone_number: str
    priority: Optional[int] = 1
    is_active: Optional[bool] = True
    role: Optional[str] = None
    department: Optional[str] = None
    group_ids: List[str]


class ContactCreate(ContactBase):
    id: str


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    department: Optional[str] = None
    group_ids: Optional[List[str]] = None


class ContactResponse(ContactBase):
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