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
    async def get_total_count(db: asyncpg.Connection) -> int:
        query = "SELECT COUNT(*) FROM contacts"
        return await db.fetchval(query)
    
    @staticmethod
    async def search_contacts(
        db: asyncpg.Connection, 
        search_query: str = None,
        name_filter: str = None,
        phone_filter: str = None,
        role_filter: str = None,
        department_filter: str = None,
        is_active: bool = None,
        priority_min: int = None,
        priority_max: int = None,
        group_id: str = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[ContactResponse]:
        """Search contacts with multiple filters"""
        base_query = """
            SELECT id, name, phone_number, priority, is_active, role, department, group_ids, created_at, updated_at
            FROM contacts
        """
        
        conditions = []
        params = []
        param_counter = 1
        
        # General search query (searches in name, phone, role, department)
        if search_query:
            search_condition = f"""(
                LOWER(name) LIKE LOWER(${param_counter}) OR 
                LOWER(phone_number) LIKE LOWER(${param_counter}) OR
                LOWER(role) LIKE LOWER(${param_counter}) OR
                LOWER(department) LIKE LOWER(${param_counter})
            )"""
            conditions.append(search_condition)
            params.append(f"%{search_query}%")
            param_counter += 1
        
        # Specific field filters
        if name_filter:
            conditions.append(f"LOWER(name) LIKE LOWER(${param_counter})")
            params.append(f"%{name_filter}%")
            param_counter += 1
            
        if phone_filter:
            conditions.append(f"phone_number LIKE ${param_counter}")
            params.append(f"%{phone_filter}%")
            param_counter += 1
            
        if role_filter:
            conditions.append(f"LOWER(role) LIKE LOWER(${param_counter})")
            params.append(f"%{role_filter}%")
            param_counter += 1
            
        if department_filter:
            conditions.append(f"LOWER(department) LIKE LOWER(${param_counter})")
            params.append(f"%{department_filter}%")
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
            
        if group_id:
            conditions.append(f"${param_counter} = ANY(group_ids)")
            params.append(group_id)
            param_counter += 1
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
            
        base_query += f" ORDER BY priority ASC, created_at DESC OFFSET ${param_counter} LIMIT ${param_counter + 1}"
        params.extend([skip, limit])
        
        rows = await db.fetch(base_query, *params)
        return [ContactResponse(**dict(row)) for row in rows]
    
    @staticmethod
    async def get_search_count(
        db: asyncpg.Connection, 
        search_query: str = None,
        name_filter: str = None,
        phone_filter: str = None,
        role_filter: str = None,
        department_filter: str = None,
        is_active: bool = None,
        priority_min: int = None,
        priority_max: int = None,
        group_id: str = None
    ) -> int:
        """Get count of contacts matching search criteria"""
        base_query = "SELECT COUNT(*) FROM contacts"
        
        conditions = []
        params = []
        param_counter = 1
        
        # General search query (searches in name, phone, role, department)
        if search_query:
            search_condition = f"""(
                LOWER(name) LIKE LOWER(${param_counter}) OR 
                LOWER(phone_number) LIKE LOWER(${param_counter}) OR
                LOWER(role) LIKE LOWER(${param_counter}) OR
                LOWER(department) LIKE LOWER(${param_counter})
            )"""
            conditions.append(search_condition)
            params.append(f"%{search_query}%")
            param_counter += 1
        
        # Specific field filters
        if name_filter:
            conditions.append(f"LOWER(name) LIKE LOWER(${param_counter})")
            params.append(f"%{name_filter}%")
            param_counter += 1
            
        if phone_filter:
            conditions.append(f"phone_number LIKE ${param_counter}")
            params.append(f"%{phone_filter}%")
            param_counter += 1
            
        if role_filter:
            conditions.append(f"LOWER(role) LIKE LOWER(${param_counter})")
            params.append(f"%{role_filter}%")
            param_counter += 1
            
        if department_filter:
            conditions.append(f"LOWER(department) LIKE LOWER(${param_counter})")
            params.append(f"%{department_filter}%")
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
            
        if group_id:
            conditions.append(f"${param_counter} = ANY(group_ids)")
            params.append(group_id)
            param_counter += 1
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
            
        return await db.fetchval(base_query, *params)
    
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