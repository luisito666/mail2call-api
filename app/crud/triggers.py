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
    async def get_total_count(db: asyncpg.Connection) -> int:
        query = "SELECT COUNT(*) FROM triggers"
        return await db.fetchval(query)
    
    @staticmethod
    async def search_triggers(
        db: asyncpg.Connection, 
        search_query: str = None,
        name_filter: str = None,
        trigger_string_filter: str = None,
        description_filter: str = None,
        group_id: str = None,
        is_active: bool = None,
        priority_min: int = None,
        priority_max: int = None,
        custom_message_filter: str = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[TriggerResponse]:
        """Search triggers with multiple filters"""
        base_query = """
            SELECT id, name, trigger_string, description, group_id, is_active, priority, custom_message, created_at, updated_at
            FROM triggers
        """
        
        conditions = []
        params = []
        param_counter = 1
        
        # General search query (searches in name, trigger_string, description, custom_message)
        if search_query:
            search_condition = f"""(
                LOWER(name) LIKE LOWER(${param_counter}) OR 
                LOWER(trigger_string) LIKE LOWER(${param_counter}) OR
                LOWER(description) LIKE LOWER(${param_counter}) OR
                LOWER(custom_message) LIKE LOWER(${param_counter})
            )"""
            conditions.append(search_condition)
            params.append(f"%{search_query}%")
            param_counter += 1
        
        # Specific field filters
        if name_filter:
            conditions.append(f"LOWER(name) LIKE LOWER(${param_counter})")
            params.append(f"%{name_filter}%")
            param_counter += 1
            
        if trigger_string_filter:
            conditions.append(f"LOWER(trigger_string) LIKE LOWER(${param_counter})")
            params.append(f"%{trigger_string_filter}%")
            param_counter += 1
            
        if description_filter:
            conditions.append(f"LOWER(description) LIKE LOWER(${param_counter})")
            params.append(f"%{description_filter}%")
            param_counter += 1
            
        if custom_message_filter:
            conditions.append(f"LOWER(custom_message) LIKE LOWER(${param_counter})")
            params.append(f"%{custom_message_filter}%")
            param_counter += 1
            
        if group_id:
            conditions.append(f"group_id = ${param_counter}")
            params.append(group_id)
            param_counter += 1
            
        if is_active is not None:
            conditions.append(f"is_active = ${param_counter}")
            params.append(is_active)
            param_counter += 1
            
        if priority_min is not None:
            conditions.append(f"priority >= ${param_counter}")
            params.append(priority_min)
            param_counter += 1
            
        if priority_max is not None:
            conditions.append(f"priority <= ${param_counter}")
            params.append(priority_max)
            param_counter += 1
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
            
        base_query += f" ORDER BY priority ASC, created_at DESC OFFSET ${param_counter} LIMIT ${param_counter + 1}"
        params.extend([skip, limit])
        
        rows = await db.fetch(base_query, *params)
        return [TriggerResponse(**dict(row)) for row in rows]
    
    @staticmethod
    async def get_search_count(
        db: asyncpg.Connection, 
        search_query: str = None,
        name_filter: str = None,
        trigger_string_filter: str = None,
        description_filter: str = None,
        group_id: str = None,
        is_active: bool = None,
        priority_min: int = None,
        priority_max: int = None,
        custom_message_filter: str = None
    ) -> int:
        """Get count of triggers matching search criteria"""
        base_query = "SELECT COUNT(*) FROM triggers"
        
        conditions = []
        params = []
        param_counter = 1
        
        # General search query (searches in name, trigger_string, description, custom_message)
        if search_query:
            search_condition = f"""(
                LOWER(name) LIKE LOWER(${param_counter}) OR 
                LOWER(trigger_string) LIKE LOWER(${param_counter}) OR
                LOWER(description) LIKE LOWER(${param_counter}) OR
                LOWER(custom_message) LIKE LOWER(${param_counter})
            )"""
            conditions.append(search_condition)
            params.append(f"%{search_query}%")
            param_counter += 1
        
        # Specific field filters
        if name_filter:
            conditions.append(f"LOWER(name) LIKE LOWER(${param_counter})")
            params.append(f"%{name_filter}%")
            param_counter += 1
            
        if trigger_string_filter:
            conditions.append(f"LOWER(trigger_string) LIKE LOWER(${param_counter})")
            params.append(f"%{trigger_string_filter}%")
            param_counter += 1
            
        if description_filter:
            conditions.append(f"LOWER(description) LIKE LOWER(${param_counter})")
            params.append(f"%{description_filter}%")
            param_counter += 1
            
        if custom_message_filter:
            conditions.append(f"LOWER(custom_message) LIKE LOWER(${param_counter})")
            params.append(f"%{custom_message_filter}%")
            param_counter += 1
            
        if group_id:
            conditions.append(f"group_id = ${param_counter}")
            params.append(group_id)
            param_counter += 1
            
        if is_active is not None:
            conditions.append(f"is_active = ${param_counter}")
            params.append(is_active)
            param_counter += 1
            
        if priority_min is not None:
            conditions.append(f"priority >= ${param_counter}")
            params.append(priority_min)
            param_counter += 1
            
        if priority_max is not None:
            conditions.append(f"priority <= ${param_counter}")
            params.append(priority_max)
            param_counter += 1
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
            
        return await db.fetchval(base_query, *params)
    
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