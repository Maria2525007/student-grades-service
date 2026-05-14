from fastapi import APIRouter, Depends

from app.dependencies import get_pool

router = APIRouter(prefix="/students")


@router.get("/more-than-3-twos")
async def more_than_3_twos(pool=Depends(get_pool)):
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT s.full_name, COUNT(*) AS count_twos
            FROM grades g
            JOIN students s ON s.id = g.student_id
            WHERE g.grade = 2
            GROUP BY s.full_name
            HAVING COUNT(*) > 3
            ORDER BY count_twos DESC, s.full_name
            """
        )
    return [{"full_name": r["full_name"], "count_twos": r["count_twos"]} for r in rows]


@router.get("/less-than-5-twos")
async def less_than_5_twos(pool=Depends(get_pool)):
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT s.full_name, COUNT(*) AS count_twos
            FROM grades g
            JOIN students s ON s.id = g.student_id
            WHERE g.grade = 2
            GROUP BY s.full_name
            HAVING COUNT(*) < 5
            ORDER BY count_twos DESC, s.full_name
            """
        )
    return [{"full_name": r["full_name"], "count_twos": r["count_twos"]} for r in rows]
