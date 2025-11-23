import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base
from app.models import User, Paste
from app.core.config import get_settings

settings = get_settings()


@pytest_asyncio.fixture
async def test_db():
    """Create test database and tables"""
    engine = create_async_engine(settings.TEST_DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_user(test_db):
    """Test user creation"""
    user = User(email="test@example.com", hashed_password="hashedpw123")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.created_at is not None


@pytest.mark.asyncio
async def test_create_paste(test_db):
    """Test paste creation"""
    paste = Paste(
        title="Test Paste", content="Hello World", short_url="abc123", language="python"
    )
    test_db.add(paste)
    await test_db.commit()
    await test_db.refresh(paste)

    assert paste.id is not None
    assert paste.title == "Test Paste"
    assert paste.view_count == 0


@pytest.mark.asyncio
async def test_user_paste_relationship(test_db):
    """Test User-Paste relationship"""
    user = User(email="owner@example.com", hashed_password="hash123")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    paste = Paste(
        title="User's Paste",
        content="Test content",
        short_url="xyz789",
        user_id=user.id,
    )
    test_db.add(paste)
    await test_db.commit()

    # Refresh to load relationships
    await test_db.refresh(user, ["pastes"])

    assert len(user.pastes) == 1
    assert user.pastes[0].title == "User's Paste"
