import asyncpg
from typing import List, Optional
from app.schemas.contact_groups import ContactGroupCreate, ContactGroupUpdate, ContactGroupResponse


class ContactGroupCRUD:
    
    @staticmethod
    async def create(db: asyncpg.Connection, contact_group: ContactGroupCreate) -> ContactGroupResponse:
        query = """
            INSERT INTO contact_groups (id, name, description, is_active, emergency_level)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, name, description, is_active, emergency_level, created_at, updated_at
        """
        row = await db.fetchrow(
            query,
            contact_group.id,
            contact_group.name,
            contact_group.description,
            contact_group.is_active,
            contact_group.emergency_level
        )
        return ContactGroupResponse(**dict(row))
    
    @staticmethod
    async def get_by_id(db: asyncpg.Connection, contact_group_id: str) -> Optional[ContactGroupResponse]:
        query = """
            SELECT id, name, description, is_active, emergency_level, created_at, updated_at
            FROM contact_groups
            WHERE id = $1
        """
        row = await db.fetchrow(query, contact_group_id)
        return ContactGroupResponse(**dict(row)) if row else None
    
    @staticmethod
    async def get_all(db: asyncpg.Connection, skip: int = 0, limit: int = 100) -> List[ContactGroupResponse]:
        query = """
            SELECT id, name, description, is_active, emergency_level, created_at, updated_at
            FROM contact_groups
            ORDER BY created_at DESC
            OFFSET $1 LIMIT $2
        """
        rows = await db.fetch(query, skip, limit)
        return [ContactGroupResponse(**dict(row)) for row in rows]
    
    @staticmethod
    async def get_total_count(db: asyncpg.Connection) -> int:
        query = "SELECT COUNT(*) FROM contact_groups"
        return await db.fetchval(query)
    
    @staticmethod
    async def search_contact_groups(
        db: asyncpg.Connection, 
        search_query: str = None,
        name_filter: str = None,
        description_filter: str = None,
        emergency_level: str = None,
        is_active: bool = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[ContactGroupResponse]:
        """Search contact groups with multiple filters"""
        base_query = """
            SELECT id, name, description, is_active, emergency_level, created_at, updated_at
            FROM contact_groups
        """
        
        conditions = []
        params = []
        param_counter = 1
        
        # General search query (searches in name and description)
        if search_query:
            search_condition = f"""(
                LOWER(name) LIKE LOWER(${param_counter}) OR 
                LOWER(description) LIKE LOWER(${param_counter})
            )"""
            conditions.append(search_condition)
            params.append(f"%{search_query}%")
            param_counter += 1
        
        # Specific field filters
        if name_filter:
            conditions.append(f"LOWER(name) LIKE LOWER(${param_counter})")
            params.append(f"%{name_filter}%")
            param_counter += 1
            
        if description_filter:
            conditions.append(f"LOWER(description) LIKE LOWER(${param_counter})")
            params.append(f"%{description_filter}%")
            param_counter += 1
            
        if emergency_level:
            conditions.append(f"LOWER(emergency_level) = LOWER(${param_counter})")
            params.append(emergency_level)
            param_counter += 1
            
        if is_active is not None:
            conditions.append(f"is_active = ${param_counter}")
            params.append(is_active)
            param_counter += 1
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
            
        base_query += f" ORDER BY created_at DESC OFFSET ${param_counter} LIMIT ${param_counter + 1}"
        params.extend([skip, limit])
        
        rows = await db.fetch(base_query, *params)
        return [ContactGroupResponse(**dict(row)) for row in rows]
    
    @staticmethod
    async def get_search_count(
        db: asyncpg.Connection, 
        search_query: str = None,
        name_filter: str = None,
        description_filter: str = None,
        emergency_level: str = None,
        is_active: bool = None
    ) -> int:
        """Get count of contact groups matching search criteria"""
        base_query = "SELECT COUNT(*) FROM contact_groups"
        
        conditions = []
        params = []
        param_counter = 1
        
        # General search query (searches in name and description)
        if search_query:
            search_condition = f"""(
                LOWER(name) LIKE LOWER(${param_counter}) OR 
                LOWER(description) LIKE LOWER(${param_counter})
            )"""
            conditions.append(search_condition)
            params.append(f"%{search_query}%")
            param_counter += 1
        
        # Specific field filters
        if name_filter:
            conditions.append(f"LOWER(name) LIKE LOWER(${param_counter})")
            params.append(f"%{name_filter}%")
            param_counter += 1
            
        if description_filter:
            conditions.append(f"LOWER(description) LIKE LOWER(${param_counter})")
            params.append(f"%{description_filter}%")
            param_counter += 1
            
        if emergency_level:
            conditions.append(f"LOWER(emergency_level) = LOWER(${param_counter})")
            params.append(emergency_level)
            param_counter += 1
            
        if is_active is not None:
            conditions.append(f"is_active = ${param_counter}")
            params.append(is_active)
            param_counter += 1
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
            
        return await db.fetchval(base_query, *params)
    
    @staticmethod
    async def update(db: asyncpg.Connection, contact_group_id: str, contact_group_update: ContactGroupUpdate) -> Optional[ContactGroupResponse]:
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        param_counter = 1
        
        for field, value in contact_group_update.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = ${param_counter}")
            values.append(value)
            param_counter += 1
        
        if not update_fields:
            return await ContactGroupCRUD.get_by_id(db, contact_group_id)
        
        query = f"""
            UPDATE contact_groups
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ${param_counter}
            RETURNING id, name, description, is_active, emergency_level, created_at, updated_at
        """
        values.append(contact_group_id)
        
        row = await db.fetchrow(query, *values)
        return ContactGroupResponse(**dict(row)) if row else None
    
    @staticmethod
    async def delete(db: asyncpg.Connection, contact_group_id: str) -> bool:
        query = "DELETE FROM contact_groups WHERE id = $1"
        result = await db.execute(query, contact_group_id)
        return result == "DELETE 1"