from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_pool
from app.routers import upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await create_pool()
    yield
    await app.state.pool.close()


app = FastAPI(title="Student Grades Service", lifespan=lifespan)

app.include_router(upload.router)
