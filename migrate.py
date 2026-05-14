import asyncio
from pathlib import Path

import asyncpg
from app.config import settings

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


async def main() -> None:
    conn = await asyncpg.connect(settings.database_url)
    try:
        for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            print(f"Applying {sql_file.name}...")
            await conn.execute(sql_file.read_text(encoding="utf-8"))
            print(f"  OK")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
