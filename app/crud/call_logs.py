import asyncpg
from typing import List, Optional
from app.schemas.call_logs import CallLogCreate, CallLogUpdate, CallLogResponse


class CallLogCRUD:
    
    @staticmethod
    async def create(db: asyncpg.Connection, call_log: CallLogCreate) -> CallLogResponse:
        query = """
            INSERT INTO call_logs (email_event_id, contact_id, phone_number, call_sid, status, duration, attempt_number, error_message)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, email_event_id, contact_id, phone_number, call_sid, status, duration, attempt_number, error_message, created_at, updated_at
        """
        row = await db.fetchrow(
            query,
            call_log.email_event_id,
            call_log.contact_id,
            call_log.phone_number,
            call_log.call_sid,
            call_log.status,
            call_log.duration,
            call_log.attempt_number,
            call_log.error_message
        )
        return CallLogResponse(**dict(row))
    
    @staticmethod
    async def get_by_id(db: asyncpg.Connection, call_log_id: int) -> Optional[CallLogResponse]:
        query = """
            SELECT id, email_event_id, contact_id, phone_number, call_sid, status, duration, attempt_number, error_message, created_at, updated_at
            FROM call_logs
            WHERE id = $1
        """
        row = await db.fetchrow(query, call_log_id)
        return CallLogResponse(**dict(row)) if row else None
    
    @staticmethod
    async def get_all(db: asyncpg.Connection, skip: int = 0, limit: int = 100) -> List[CallLogResponse]:
        query = """
            SELECT id, email_event_id, contact_id, phone_number, call_sid, status, duration, attempt_number, error_message, created_at, updated_at
            FROM call_logs
            ORDER BY created_at DESC
            OFFSET $1 LIMIT $2
        """
        rows = await db.fetch(query, skip, limit)
        return [CallLogResponse(**dict(row)) for row in rows]
    
    @staticmethod
    async def get_total_count(db: asyncpg.Connection) -> int:
        query = "SELECT COUNT(*) FROM call_logs"
        return await db.fetchval(query)
    
    @staticmethod
    async def get_by_email_event_id(db: asyncpg.Connection, email_event_id: str) -> List[CallLogResponse]:
        query = """
            SELECT id, email_event_id, contact_id, phone_number, call_sid, status, duration, attempt_number, error_message, created_at, updated_at
            FROM call_logs
            WHERE email_event_id = $1
            ORDER BY attempt_number ASC, created_at ASC
        """
        rows = await db.fetch(query, email_event_id)
        return [CallLogResponse(**dict(row)) for row in rows]
    
    @staticmethod
    async def get_by_contact_id(db: asyncpg.Connection, contact_id: str) -> List[CallLogResponse]:
        query = """
            SELECT id, email_event_id, contact_id, phone_number, call_sid, status, duration, attempt_number, error_message, created_at, updated_at
            FROM call_logs
            WHERE contact_id = $1
            ORDER BY created_at DESC
        """
        rows = await db.fetch(query, contact_id)
        return [CallLogResponse(**dict(row)) for row in rows]
    
    @staticmethod
    async def update(db: asyncpg.Connection, call_log_id: int, call_log_update: CallLogUpdate) -> Optional[CallLogResponse]:
        update_fields = []
        values = []
        param_counter = 1
        
        for field, value in call_log_update.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = ${param_counter}")
            values.append(value)
            param_counter += 1
        
        if not update_fields:
            return await CallLogCRUD.get_by_id(db, call_log_id)
        
        query = f"""
            UPDATE call_logs
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ${param_counter}
            RETURNING id, email_event_id, contact_id, phone_number, call_sid, status, duration, attempt_number, error_message, created_at, updated_at
        """
        values.append(call_log_id)
        
        row = await db.fetchrow(query, *values)
        return CallLogResponse(**dict(row)) if row else None
    
    @staticmethod
    async def delete(db: asyncpg.Connection, call_log_id: int) -> bool:
        query = "DELETE FROM call_logs WHERE id = $1"
        result = await db.execute(query, call_log_id)
        return result == "DELETE 1"