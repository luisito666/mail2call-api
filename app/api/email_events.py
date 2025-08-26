from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
import math
from app.database.connection import get_db_connection
from app.crud.email_events import EmailEventCRUD
from app.schemas.email_events import EmailEventCreate, EmailEventUpdate, EmailEventResponse, PaginatedResponse
from app.core.auth import get_current_user

router = APIRouter(prefix="/email-events", tags=["email-events"])


@router.post("/", response_model=EmailEventResponse, status_code=status.HTTP_201_CREATED)
async def create_email_event(
    email_event: EmailEventCreate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    try:
        return await EmailEventCRUD.create(db, email_event)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{email_event_id}", response_model=EmailEventResponse)
async def get_email_event(
    email_event_id: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    email_event = await EmailEventCRUD.get_by_id(db, email_event_id)
    if not email_event:
        raise HTTPException(status_code=404, detail="Email event not found")
    return email_event


@router.get("/", response_model=PaginatedResponse[EmailEventResponse])
async def get_email_events(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    skip = (page - 1) * per_page
    
    # Get total count and items in parallel
    total = await EmailEventCRUD.get_total_count(db)
    items = await EmailEventCRUD.get_all(db, skip, per_page)
    
    total_pages = math.ceil(total / per_page)
    
    return PaginatedResponse[EmailEventResponse](
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/by-status/{status}", response_model=List[EmailEventResponse])
async def get_email_events_by_status(
    status: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    return await EmailEventCRUD.get_by_status(db, status)


@router.get("/by-trigger/{trigger_matched}", response_model=List[EmailEventResponse])
async def get_email_events_by_trigger(
    trigger_matched: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    return await EmailEventCRUD.get_by_trigger(db, trigger_matched)


@router.put("/{email_event_id}", response_model=EmailEventResponse)
async def update_email_event(
    email_event_id: str,
    email_event_update: EmailEventUpdate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    email_event = await EmailEventCRUD.update(db, email_event_id, email_event_update)
    if not email_event:
        raise HTTPException(status_code=404, detail="Email event not found")
    return email_event


@router.delete("/{email_event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email_event(
    email_event_id: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    deleted = await EmailEventCRUD.delete(db, email_event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Email event not found")