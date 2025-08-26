from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
import math
from app.database.connection import get_db_connection
from app.crud.contacts import ContactCRUD
from app.schemas.contacts import ContactCreate, ContactUpdate, ContactResponse, PaginatedResponse
from app.core.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact: ContactCreate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    try:
        return await ContactCRUD.create(db, contact)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    contact = await ContactCRUD.get_by_id(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.get("/", response_model=PaginatedResponse[ContactResponse])
async def get_contacts(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    skip = (page - 1) * per_page
    
    # Get total count and items in parallel
    total = await ContactCRUD.get_total_count(db)
    items = await ContactCRUD.get_all(db, skip, per_page)
    
    total_pages = math.ceil(total / per_page)
    
    return PaginatedResponse[ContactResponse](
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/by-group/{group_id}", response_model=List[ContactResponse])
async def get_contacts_by_group(
    group_id: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    return await ContactCRUD.get_by_group_id(db, group_id)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: str,
    contact_update: ContactUpdate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    contact = await ContactCRUD.update(db, contact_id, contact_update)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    deleted = await ContactCRUD.delete(db, contact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")