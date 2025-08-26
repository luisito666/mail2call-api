import asyncpg
from typing import List, Optional
from app.schemas.email_events import EmailEventCreate, EmailEventUpdate, EmailEventResponse


class EmailEventCRUD:
    
    @staticmethod
    async def create(db: asyncpg.Connection, email_event: EmailEventCreate) -> EmailEventResponse:
        query = """
            INSERT INTO email_events (id, from_email, subject, body, trigger_matched, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, from_email, subject, body, trigger_matched, received_at, processed_at, status
        """
        row = await db.fetchrow(
            query,
            email_event.id,
            email_event.from_email,
            email_event.subject,
            email_event.body,
            email_event.trigger_matched,
            email_event.status
        )
        return EmailEventResponse(**dict(row))
    
    @staticmethod
    async def get_by_id(db: asyncpg.Connection, email_event_id: str) -> Optional[EmailEventResponse]:
        query = """
            SELECT id, from_email, subject, body, trigger_matched, received_at, processed_at, status
            FROM email_events
            WHERE id = $1
        """
        row = await db.fetchrow(query, email_event_id)
        return EmailEventResponse(**dict(row)) if row else None
    
    @staticmethod
    async def get_all(db: asyncpg.Connection, skip: int = 0, limit: int = 100) -> List[EmailEventResponse]:
        query = """
            SELECT id, from_email, subject, body, trigger_matched, received_at, processed_at, status
            FROM email_events
            ORDER BY received_at DESC
            OFFSET $1 LIMIT $2
        """
        rows = await db.fetch(query, skip, limit)
        return [EmailEventResponse(**dict(row)) for row in rows]
    
    @staticmethod
    async def get_total_count(db: asyncpg.Connection) -> int:
        query = "SELECT COUNT(*) FROM email_events"
        return await db.fetchval(query)
    
    @staticmethod
    async def get_by_status(db: asyncpg.Connection, status: str) -> List[EmailEventResponse]:
        query = """
            SELECT id, from_email, subject, body, trigger_matched, received_at, processed_at, status
            FROM email_events
            WHERE status = $1
            ORDER BY received_at DESC
        """
        rows = await db.fetch(query, status)
        return [EmailEventResponse(**dict(row)) for row in rows]
    
    @staticmethod
    async def get_by_trigger(db: asyncpg.Connection, trigger_matched: str) -> List[EmailEventResponse]:
        query = """
            SELECT id, from_email, subject, body, trigger_matched, received_at, processed_at, status
            FROM email_events
            WHERE trigger_matched = $1
            ORDER BY received_at DESC
        """
        rows = await db.fetch(query, trigger_matched)
        return [EmailEventResponse(**dict(row)) for row in rows]
    
    @staticmethod
    async def update(db: asyncpg.Connection, email_event_id: str, email_event_update: EmailEventUpdate) -> Optional[EmailEventResponse]:
        update_fields = []
        values = []
        param_counter = 1
        
        update_data = email_event_update.dict(exclude_unset=True)
        
        # Handle processed_at field specially if status is being updated to 'processed'
        if 'status' in update_data and update_data['status'] == 'processed':
            update_fields.append(f"processed_at = CURRENT_TIMESTAMP")
        
        for field, value in update_data.items():
            update_fields.append(f"{field} = ${param_counter}")
            values.append(value)
            param_counter += 1
        
        if not update_fields:
            return await EmailEventCRUD.get_by_id(db, email_event_id)
        
        query = f"""
            UPDATE email_events
            SET {', '.join(update_fields)}
            WHERE id = ${param_counter}
            RETURNING id, from_email, subject, body, trigger_matched, received_at, processed_at, status
        """
        values.append(email_event_id)
        
        row = await db.fetchrow(query, *values)
        return EmailEventResponse(**dict(row)) if row else None
    
    @staticmethod
    async def delete(db: asyncpg.Connection, email_event_id: str) -> bool:
        query = "DELETE FROM email_events WHERE id = $1"
        result = await db.execute(query, email_event_id)
        return result == "DELETE 1"