from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from .config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, autocommit=False)
Base = declarative_base()

async def get_db():
    """
    Creates an async database session for each request and closes it when done.
    """
    async with AsyncSessionLocal() as session:
        yield session
