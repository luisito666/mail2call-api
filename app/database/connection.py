import asyncpg
from typing import Optional
from app.core.config import settings

_pool: Optional[asyncpg.Pool] = None


async def init_db_pool():
    global _pool
    _pool = await asyncpg.create_pool(settings.database_url)
    

async def get_db_pool() -> asyncpg.Pool:
    if _pool is None:
        await init_db_pool()
    return _pool


async def close_db_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def get_db_connection():
    pool = await get_db_pool()
    async with pool.acquire() as connection:
        yield connection