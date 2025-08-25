from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.database.connection import get_db_connection
from app.crud.system_stats import SystemStatsCRUD
from app.schemas.system_stats import SystemStatsCreate, SystemStatsUpdate, SystemStatsResponse
from app.core.auth import get_current_user

router = APIRouter(prefix="/system-stats", tags=["system-stats"])


@router.post("/", response_model=SystemStatsResponse, status_code=status.HTTP_201_CREATED)
async def create_system_stats(
    system_stats: SystemStatsCreate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    try:
        return await SystemStatsCRUD.create(db, system_stats)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{stats_id}", response_model=SystemStatsResponse)
async def get_system_stats(
    stats_id: int,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    stats = await SystemStatsCRUD.get_by_id(db, stats_id)
    if not stats:
        raise HTTPException(status_code=404, detail="System stats not found")
    return stats


@router.get("/", response_model=List[SystemStatsResponse])
async def get_all_system_stats(
    skip: int = 0,
    limit: int = 100,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    return await SystemStatsCRUD.get_all(db, skip, limit)


@router.get("/by-metric/{metric_name}", response_model=List[SystemStatsResponse])
async def get_system_stats_by_metric(
    metric_name: str,
    skip: int = 0,
    limit: int = 100,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    return await SystemStatsCRUD.get_by_metric_name(db, metric_name, skip, limit)


@router.get("/latest/{metric_name}", response_model=SystemStatsResponse)
async def get_latest_system_stats(
    metric_name: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    stats = await SystemStatsCRUD.get_latest_by_metric_name(db, metric_name)
    if not stats:
        raise HTTPException(status_code=404, detail="System stats not found")
    return stats


@router.put("/{stats_id}", response_model=SystemStatsResponse)
async def update_system_stats(
    stats_id: int,
    system_stats_update: SystemStatsUpdate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    stats = await SystemStatsCRUD.update(db, stats_id, system_stats_update)
    if not stats:
        raise HTTPException(status_code=404, detail="System stats not found")
    return stats


@router.delete("/{stats_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system_stats(
    stats_id: int,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    deleted = await SystemStatsCRUD.delete(db, stats_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="System stats not found")


@router.delete("/cleanup/{days_to_keep}")
async def cleanup_old_stats(
    days_to_keep: int = 30,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    deleted_count = await SystemStatsCRUD.delete_old_stats(db, days_to_keep)
    return {"message": f"Deleted {deleted_count} old system stats records"}


@router.get("/counts/active-triggers")
async def get_active_triggers_count(
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    count = await SystemStatsCRUD.get_active_triggers_count(db)
    return {"total_active_triggers": count}


@router.get("/counts/contacts")
async def get_contacts_count(
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    count = await SystemStatsCRUD.get_contacts_count(db)
    return {"total_contacts": count}


@router.get("/counts/contact-groups")
async def get_contact_groups_count(
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    count = await SystemStatsCRUD.get_contact_groups_count(db)
    return {"total_contact_groups": count}


@router.get("/counts/daily-calls")
async def get_daily_calls_count(
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    count = await SystemStatsCRUD.get_daily_calls_count(db)
    return {"total_daily_calls": count}