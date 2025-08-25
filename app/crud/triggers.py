import asyncpg
from typing import List, Optional
from app.schemas.triggers import TriggerCreate, TriggerUpdate, TriggerResponse


class TriggerCRUD:
    
    @staticmethod
    async def create(db: asyncpg.Connection, trigger: TriggerCreate) -> TriggerResponse:
        query = """
            INSERT INTO triggers (id, name, trigger_string, description, group_id, is_active, priority, custom_message)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, name, trigger_string, description, group_id, is_active, priority, custom_message, created_at, updated_at
        """
        row = await db.fetchrow(
            query,
            trigger.id,
            trigger.name,
            trigger.trigger_string,
            trigger.description,
            trigger.group_id,
            trigger.is_active,
            trigger.priority,
            trigger.custom_message
        )
        return TriggerResponse(**dict(row))
    
    @staticmethod
    async def get_by_id(db: asyncpg.Connection, trigger_id: str) -> Optional[TriggerResponse]:
        query = """
            SELECT id, name, trigger_string, description, group_id, is_active, priority, custom_message, created_at, updated_at
            FROM triggers
            WHERE id = $1
        """
        row = await db.fetchrow(query, trigger_id)
        return TriggerResponse(**dict(row)) if row else None
    
    @staticmethod
    async def get_all(db: asyncpg.Connection, skip: int = 0, limit: int = 100) -> List[TriggerResponse]:
        query = """
            SELECT id, name, trigger_string, description, group_id, is_active, priority, custom_message, created_at, updated_at
            FROM triggers
            ORDER BY priority ASC, created_at DESC
            OFFSET $1 LIMIT $2
        """
        rows = await db.fetch(query, skip, limit)
        return [TriggerResponse(**dict(row)) for row in rows]
    
    @staticmethod
    async def get_by_trigger_string(db: asyncpg.Connection, trigger_string: str) -> Optional[TriggerResponse]:
        query = """
            SELECT id, name, trigger_string, description, group_id, is_active, priority, custom_message, created_at, updated_at
            FROM triggers
            WHERE trigger_string = $1 AND is_active = true
        """
        row = await db.fetchrow(query, trigger_string)
        return TriggerResponse(**dict(row)) if row else None
    
    @staticmethod
    async def update(db: asyncpg.Connection, trigger_id: str, trigger_update: TriggerUpdate) -> Optional[TriggerResponse]:
        update_fields = []
        values = []
        param_counter = 1
        
        for field, value in trigger_update.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = ${param_counter}")
            values.append(value)
            param_counter += 1
        
        if not update_fields:
            return await TriggerCRUD.get_by_id(db, trigger_id)
        
        query = f"""
            UPDATE triggers
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ${param_counter}
            RETURNING id, name, trigger_string, description, group_id, is_active, priority, custom_message, created_at, updated_at
        """
        values.append(trigger_id)
        
        row = await db.fetchrow(query, *values)
        return TriggerResponse(**dict(row)) if row else None
    
    @staticmethod
    async def delete(db: asyncpg.Connection, trigger_id: str) -> bool:
        query = "DELETE FROM triggers WHERE id = $1"
        result = await db.execute(query, trigger_id)
        return result == "DELETE 1"