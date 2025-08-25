import asyncpg
from typing import List, Optional
from app.schemas.contacts import ContactCreate, ContactUpdate, ContactResponse


class ContactCRUD:
    
    @staticmethod
    async def create(db: asyncpg.Connection, contact: ContactCreate) -> ContactResponse:
        query = """
            INSERT INTO contacts (id, name, phone_number, priority, is_active, role, department, group_ids)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, name, phone_number, priority, is_active, role, department, group_ids, created_at, updated_at
        """
        row = await db.fetchrow(
            query,
            contact.id,
            contact.name,
            contact.phone_number,
            contact.priority,
            contact.is_active,
            contact.role,
            contact.department,
            contact.group_ids
        )
        return ContactResponse(**dict(row))
    
    @staticmethod
    async def get_by_id(db: asyncpg.Connection, contact_id: str) -> Optional[ContactResponse]:
        query = """
            SELECT id, name, phone_number, priority, is_active, role, department, group_ids, created_at, updated_at
            FROM contacts
            WHERE id = $1
        """
        row = await db.fetchrow(query, contact_id)
        return ContactResponse(**dict(row)) if row else None
    
    @staticmethod
    async def get_all(db: asyncpg.Connection, skip: int = 0, limit: int = 100) -> List[ContactResponse]:
        query = """
            SELECT id, name, phone_number, priority, is_active, role, department, group_ids, created_at, updated_at
            FROM contacts
            ORDER BY priority ASC, created_at DESC
            OFFSET $1 LIMIT $2
        """
        rows = await db.fetch(query, skip, limit)
        return [ContactResponse(**dict(row)) for row in rows]
    
    @staticmethod
    async def get_by_group_id(db: asyncpg.Connection, group_id: str) -> List[ContactResponse]:
        query = """
            SELECT id, name, phone_number, priority, is_active, role, department, group_ids, created_at, updated_at
            FROM contacts
            WHERE $1 = ANY(group_ids) AND is_active = true
            ORDER BY priority ASC
        """
        rows = await db.fetch(query, group_id)
        return [ContactResponse(**dict(row)) for row in rows]
    
    @staticmethod
    async def update(db: asyncpg.Connection, contact_id: str, contact_update: ContactUpdate) -> Optional[ContactResponse]:
        update_fields = []
        values = []
        param_counter = 1
        
        for field, value in contact_update.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = ${param_counter}")
            values.append(value)
            param_counter += 1
        
        if not update_fields:
            return await ContactCRUD.get_by_id(db, contact_id)
        
        query = f"""
            UPDATE contacts
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ${param_counter}
            RETURNING id, name, phone_number, priority, is_active, role, department, group_ids, created_at, updated_at
        """
        values.append(contact_id)
        
        row = await db.fetchrow(query, *values)
        return ContactResponse(**dict(row)) if row else None
    
    @staticmethod
    async def delete(db: asyncpg.Connection, contact_id: str) -> bool:
        query = "DELETE FROM contacts WHERE id = $1"
        result = await db.execute(query, contact_id)
        return result == "DELETE 1"