from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.database.connection import get_db_connection
from app.crud.call_logs import CallLogCRUD
from app.schemas.call_logs import CallLogCreate, CallLogUpdate, CallLogResponse
from app.core.auth import get_current_user

router = APIRouter(prefix="/call-logs", tags=["call-logs"])


@router.post("/", response_model=CallLogResponse, status_code=status.HTTP_201_CREATED)
async def create_call_log(
    call_log: CallLogCreate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    try:
        return await CallLogCRUD.create(db, call_log)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{call_log_id}", response_model=CallLogResponse)
async def get_call_log(
    call_log_id: int,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    call_log = await CallLogCRUD.get_by_id(db, call_log_id)
    if not call_log:
        raise HTTPException(status_code=404, detail="Call log not found")
    return call_log


@router.get("/", response_model=List[CallLogResponse])
async def get_call_logs(
    skip: int = 0,
    limit: int = 100,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    return await CallLogCRUD.get_all(db, skip, limit)


@router.get("/by-email-event/{email_event_id}", response_model=List[CallLogResponse])
async def get_call_logs_by_email_event(
    email_event_id: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    return await CallLogCRUD.get_by_email_event_id(db, email_event_id)


@router.get("/by-contact/{contact_id}", response_model=List[CallLogResponse])
async def get_call_logs_by_contact(
    contact_id: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    return await CallLogCRUD.get_by_contact_id(db, contact_id)


@router.put("/{call_log_id}", response_model=CallLogResponse)
async def update_call_log(
    call_log_id: int,
    call_log_update: CallLogUpdate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    call_log = await CallLogCRUD.update(db, call_log_id, call_log_update)
    if not call_log:
        raise HTTPException(status_code=404, detail="Call log not found")
    return call_log


@router.delete("/{call_log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_call_log(
    call_log_id: int,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    deleted = await CallLogCRUD.delete(db, call_log_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Call log not found")