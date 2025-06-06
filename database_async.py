from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from config import settings

# Build async database URL from DATABASE_URL when ASYNC_DATABASE_URL isn't set
ASYNC_DATABASE_URL = settings.async_database_url
if not ASYNC_DATABASE_URL:
    db_url = settings.database_url
    if db_url.startswith("postgresql://"):
        ASYNC_DATABASE_URL = db_url.replace("postgresql://", "postgresql+asyncpg://")
    elif db_url.startswith("sqlite://"):
        ASYNC_DATABASE_URL = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    else:
        ASYNC_DATABASE_URL = db_url

async_engine = create_async_engine(ASYNC_DATABASE_URL, future=True)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

Base = declarative_base()


async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session


__all__ = ["async_engine", "AsyncSessionLocal", "Base", "get_async_db"]
