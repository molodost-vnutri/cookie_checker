from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from source.config import config

engine = create_async_engine(url="sqlite+aiosqlite:///database.db")

async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass

async def lifespan():
    if config.save_to == "sqlite":
        async with engine.connect() as connection:
            await connection.run_sync(Base.metadata.create_all)