"""
Database connection and session management
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    pass


# Create async engine
engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=settings.environment == "development"
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.
    Automatically handles session cleanup and error rollback.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    Use this in route dependencies.
    """
    async with get_db_session() as session:
        yield session


async def init_db() -> None:
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Import models here to avoid circular imports
        # Note: User and ApiKey models kept for schema compatibility, not used for auth
        from app.shared.models import User, ApiKey
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections"""
    await engine.dispose()


def get_pool_status() -> dict:
    """Get current connection pool status for monitoring"""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else None,
        "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else None,
        "overflow": pool.overflow() if hasattr(pool, 'overflow') else None,
        "invalid": pool.invalid() if hasattr(pool, 'invalid') else None,
    }

