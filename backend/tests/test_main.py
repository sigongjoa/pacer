import pytest
from httpx import AsyncClient

from main import app

# Test DB override (reusing from conftest)

@pytest.mark.asyncio
async def test_read_root(client_with_db: AsyncClient):
    response = await client_with_db.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Pacer API"}