import asyncpg
from typing import List, Optional
from app.schemas.system_stats import SystemStatsCreate, SystemStatsUpdate, SystemStatsResponse


class SystemStatsCRUD:
    
    @staticmethod
    async def create(db: asyncpg.Connection, system_stats: SystemStatsCreate) -> SystemStatsResponse:
        query = """
            INSERT INTO system_stats (metric_name, metric_value)
            VALUES ($1, $2)
            RETURNING id, metric_name, metric_value, recorded_at
        """
        row = await db.fetchrow(
            query,
            system_stats.metric_name,
            system_stats.metric_value
        )
        return SystemStatsResponse(**dict(row))
    
    @staticmethod
    async def get_by_id(db: asyncpg.Connection, stats_id: int) -> Optional[SystemStatsResponse]:
        query = """
            SELECT id, metric_name, metric_value, recorded_at
            FROM system_stats
            WHERE id = $1
        """
        row = await db.fetchrow(query, stats_id)
        return SystemStatsResponse(**dict(row)) if row else None
    
    @staticmethod
    async def get_all(db: asyncpg.Connection, skip: int = 0, limit: int = 100) -> List[SystemStatsResponse]:
        query = """
            SELECT id, metric_name, metric_value, recorded_at
            FROM system_stats
            ORDER BY recorded_at DESC
            OFFSET $1 LIMIT $2
        """
        rows = await db.fetch(query, skip, limit)
        return [SystemStatsResponse(**dict(row)) for row in rows]
    
    @staticmethod
    async def get_by_metric_name(db: asyncpg.Connection, metric_name: str, skip: int = 0, limit: int = 100) -> List[SystemStatsResponse]:
        query = """
            SELECT id, metric_name, metric_value, recorded_at
            FROM system_stats
            WHERE metric_name = $1
            ORDER BY recorded_at DESC
            OFFSET $2 LIMIT $3
        """
        rows = await db.fetch(query, metric_name, skip, limit)
        return [SystemStatsResponse(**dict(row)) for row in rows]
    
    @staticmethod
    async def get_latest_by_metric_name(db: asyncpg.Connection, metric_name: str) -> Optional[SystemStatsResponse]:
        query = """
            SELECT id, metric_name, metric_value, recorded_at
            FROM system_stats
            WHERE metric_name = $1
            ORDER BY recorded_at DESC
            LIMIT 1
        """
        row = await db.fetchrow(query, metric_name)
        return SystemStatsResponse(**dict(row)) if row else None
    
    @staticmethod
    async def update(db: asyncpg.Connection, stats_id: int, system_stats_update: SystemStatsUpdate) -> Optional[SystemStatsResponse]:
        update_fields = []
        values = []
        param_counter = 1
        
        for field, value in system_stats_update.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = ${param_counter}")
            values.append(value)
            param_counter += 1
        
        if not update_fields:
            return await SystemStatsCRUD.get_by_id(db, stats_id)
        
        query = f"""
            UPDATE system_stats
            SET {', '.join(update_fields)}
            WHERE id = ${param_counter}
            RETURNING id, metric_name, metric_value, recorded_at
        """
        values.append(stats_id)
        
        row = await db.fetchrow(query, *values)
        return SystemStatsResponse(**dict(row)) if row else None
    
    @staticmethod
    async def delete(db: asyncpg.Connection, stats_id: int) -> bool:
        query = "DELETE FROM system_stats WHERE id = $1"
        result = await db.execute(query, stats_id)
        return result == "DELETE 1"
    
    @staticmethod
    async def delete_old_stats(db: asyncpg.Connection, days_to_keep: int = 30) -> int:
        query = """
            DELETE FROM system_stats 
            WHERE recorded_at < NOW() - INTERVAL '%s days'
        """ % days_to_keep
        result = await db.execute(query)
        return int(result.split()[-1]) if result.startswith("DELETE") else 0
    
    @staticmethod
    async def get_active_triggers_count(db: asyncpg.Connection) -> int:
        query = "SELECT COUNT(*) FROM triggers WHERE is_active = true"
        result = await db.fetchval(query)
        return result
    
    @staticmethod
    async def get_contacts_count(db: asyncpg.Connection) -> int:
        query = "SELECT COUNT(*) FROM contacts"
        result = await db.fetchval(query)
        return result
    
    @staticmethod
    async def get_contact_groups_count(db: asyncpg.Connection) -> int:
        query = "SELECT COUNT(*) FROM contact_groups"
        result = await db.fetchval(query)
        return result
    
    @staticmethod
    async def get_daily_calls_count(db: asyncpg.Connection) -> int:
        query = """
            SELECT COUNT(*) FROM call_logs 
            WHERE DATE(created_at) = CURRENT_DATE
        """
        result = await db.fetchval(query)
        return result