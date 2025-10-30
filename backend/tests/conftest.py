import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient # httpx.AsyncClient 대신 TestClient 임포트
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from main import app
from database import Base # Import Base from your app
from llm_filter import get_db # 추가

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    # This is necessary for pytest-asyncio to manage the event loop correctly
    # for session-scoped fixtures.
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def async_engine():
    """Session-scoped fixture for the async SQLAlchemy engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) # Create tables
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # Drop tables after tests
    await engine.dispose()

@pytest.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Function-scoped fixture for a transactional async session."""
    async_session_maker = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        async with session.begin(): # Start a transaction
            yield session
            await session.rollback() # Rollback after each test to clean the state

@pytest_asyncio.fixture(scope="function")
async def client_with_db(async_session: AsyncSession):
    """
    Fixture to provide an AsyncClient with the overridden database dependency.
    """
    def override_get_db():
        yield async_session
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app) # TestClient 사용
    yield client
    app.dependency_overrides.clear() # Clear overrides after tests
