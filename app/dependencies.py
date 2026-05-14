from fastapi import Request
import asyncpg


async def get_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.pool
