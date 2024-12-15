from sqlalchemy import insert, select

from source.database import async_session
from source.models import MetadataBase


class CRUD:
    model = MetadataBase

    @classmethod
    async def find_data(cls, **kwargs):
        async with async_session() as session:
            query = select(cls.model).filter_by(**kwargs)
            result = await session.execute(query)
            return result.scalars().all()
    
    @classmethod
    async def insert_data(cls, **kwargs):
        if await cls.find_data(**kwargs):
            return
        async with async_session() as session:
            query = insert(cls.model).values(**kwargs)
            await session.execute(query)
            await session.commit()