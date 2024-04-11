import pytest
from httpx import AsyncClient

from main import app


@pytest.fixture(scope='session')
async def client():
    async with AsyncClient(app=app, base_url='http://test/v1') as ac:
        yield ac
