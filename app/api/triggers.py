from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import math
from app.database.connection import get_db_connection
from app.crud.triggers import TriggerCRUD
from app.schemas.triggers import TriggerCreate, TriggerUpdate, TriggerResponse, PaginatedResponse
from app.core.auth import get_current_user

router = APIRouter(prefix="/triggers", tags=["triggers"])


@router.post("/", response_model=TriggerResponse, status_code=status.HTTP_201_CREATED)
async def create_trigger(
    trigger: TriggerCreate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    try:
        return await TriggerCRUD.create(db, trigger)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search", response_model=PaginatedResponse[TriggerResponse])
async def search_triggers(
    # General search
    q: Optional[str] = Query(None, description="General search query (searches in name, trigger_string, description, custom_message)"),
    
    # Specific field filters
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    trigger_string: Optional[str] = Query(None, description="Filter by trigger string (partial match)"),
    description: Optional[str] = Query(None, description="Filter by description (partial match)"),
    custom_message: Optional[str] = Query(None, description="Filter by custom message (partial match)"),
    group_id: Optional[str] = Query(None, description="Filter by group ID"),
    
    # Status and priority filters
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    priority_min: Optional[int] = Query(None, ge=1, description="Minimum priority"),
    priority_max: Optional[int] = Query(None, ge=1, description="Maximum priority"),
    
    # Pagination
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    
    # Dependencies
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    """Search triggers with multiple filters and pagination"""
    skip = (page - 1) * per_page
    
    # Get search results and total count
    items = await TriggerCRUD.search_triggers(
        db=db,
        search_query=q,
        name_filter=name,
        trigger_string_filter=trigger_string,
        description_filter=description,
        custom_message_filter=custom_message,
        group_id=group_id,
        is_active=is_active,
        priority_min=priority_min,
        priority_max=priority_max,
        skip=skip,
        limit=per_page
    )
    
    total = await TriggerCRUD.get_search_count(
        db=db,
        search_query=q,
        name_filter=name,
        trigger_string_filter=trigger_string,
        description_filter=description,
        custom_message_filter=custom_message,
        group_id=group_id,
        is_active=is_active,
        priority_min=priority_min,
        priority_max=priority_max
    )
    
    total_pages = math.ceil(total / per_page)
    
    return PaginatedResponse[TriggerResponse](
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/", response_model=PaginatedResponse[TriggerResponse])
async def get_triggers(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    skip = (page - 1) * per_page
    
    # Get total count and items in parallel
    total = await TriggerCRUD.get_total_count(db)
    items = await TriggerCRUD.get_all(db, skip, per_page)
    
    total_pages = math.ceil(total / per_page)
    
    return PaginatedResponse[TriggerResponse](
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/{trigger_id}", response_model=TriggerResponse)
async def get_trigger(
    trigger_id: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    trigger = await TriggerCRUD.get_by_id(db, trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")
    return trigger


@router.get("/by-string/{trigger_string}", response_model=TriggerResponse)
async def get_trigger_by_string(
    trigger_string: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    trigger = await TriggerCRUD.get_by_trigger_string(db, trigger_string)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")
    return trigger


@router.put("/{trigger_id}", response_model=TriggerResponse)
async def update_trigger(
    trigger_id: str,
    trigger_update: TriggerUpdate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    trigger = await TriggerCRUD.update(db, trigger_id, trigger_update)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")
    return trigger


@router.delete("/{trigger_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trigger(
    trigger_id: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    deleted = await TriggerCRUD.delete(db, trigger_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Trigger not found")