from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import math
from app.database.connection import get_db_connection
from app.crud.contact_groups import ContactGroupCRUD
from app.schemas.contact_groups import ContactGroupCreate, ContactGroupUpdate, ContactGroupResponse, PaginatedResponse
from app.core.auth import get_current_user

router = APIRouter(prefix="/contact-groups", tags=["contact-groups"])


@router.post("/", response_model=ContactGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_group(
    contact_group: ContactGroupCreate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    try:
        return await ContactGroupCRUD.create(db, contact_group)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search", response_model=PaginatedResponse[ContactGroupResponse])
async def search_contact_groups(
    # General search
    q: Optional[str] = Query(None, description="General search query (searches in name and description)"),
    
    # Specific field filters
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    description: Optional[str] = Query(None, description="Filter by description (partial match)"),
    emergency_level: Optional[str] = Query(None, description="Filter by emergency level (low, medium, high, critical)"),
    
    # Status filter
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    
    # Pagination
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    
    # Dependencies
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    """Search contact groups with multiple filters and pagination"""
    skip = (page - 1) * per_page
    
    # Get search results and total count
    items = await ContactGroupCRUD.search_contact_groups(
        db=db,
        search_query=q,
        name_filter=name,
        description_filter=description,
        emergency_level=emergency_level,
        is_active=is_active,
        skip=skip,
        limit=per_page
    )
    
    total = await ContactGroupCRUD.get_search_count(
        db=db,
        search_query=q,
        name_filter=name,
        description_filter=description,
        emergency_level=emergency_level,
        is_active=is_active
    )
    
    total_pages = math.ceil(total / per_page)
    
    return PaginatedResponse[ContactGroupResponse](
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/", response_model=PaginatedResponse[ContactGroupResponse])
async def get_contact_groups(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    skip = (page - 1) * per_page
    
    # Get total count and items in parallel
    total = await ContactGroupCRUD.get_total_count(db)
    items = await ContactGroupCRUD.get_all(db, skip, per_page)
    
    total_pages = math.ceil(total / per_page)
    
    return PaginatedResponse[ContactGroupResponse](
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/{contact_group_id}", response_model=ContactGroupResponse)
async def get_contact_group(
    contact_group_id: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    contact_group = await ContactGroupCRUD.get_by_id(db, contact_group_id)
    if not contact_group:
        raise HTTPException(status_code=404, detail="Contact group not found")
    return contact_group


@router.put("/{contact_group_id}", response_model=ContactGroupResponse)
async def update_contact_group(
    contact_group_id: str,
    contact_group_update: ContactGroupUpdate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    contact_group = await ContactGroupCRUD.update(db, contact_group_id, contact_group_update)
    if not contact_group:
        raise HTTPException(status_code=404, detail="Contact group not found")
    return contact_group


@router.delete("/{contact_group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact_group(
    contact_group_id: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    deleted = await ContactGroupCRUD.delete(db, contact_group_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact group not found")