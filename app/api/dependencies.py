from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.db import engine

SessionLocal = async_sessionmaker(bind=engine)


async def get_db():
    async with SessionLocal() as db:
        yield db
