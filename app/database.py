import asyncpg
from app.config import settings


async def create_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(settings.database_url)
