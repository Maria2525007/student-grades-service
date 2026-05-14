import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies import get_pool


class FakeTransaction:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        pass


class FakeConn:
    def __init__(self, fetch_result=None):
        self._fetch_result = fetch_result or []

    async def fetch(self, *args, **kwargs):
        return self._fetch_result

    async def execute(self, *args, **kwargs):
        pass

    async def executemany(self, *args, **kwargs):
        pass

    def transaction(self):
        return FakeTransaction()


class FakeAcquire:
    def __init__(self, conn):
        self._conn = conn

    async def __aenter__(self):
        return self._conn

    async def __aexit__(self, *_):
        pass


class FakePool:
    def __init__(self, fetch_result=None):
        self._fetch_result = fetch_result or []

    def acquire(self):
        return FakeAcquire(FakeConn(fetch_result=self._fetch_result))


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


def override_pool(fetch_result=None):
    pool = FakePool(fetch_result=fetch_result)

    async def _dep():
        return pool

    return _dep
