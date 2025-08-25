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