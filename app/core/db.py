import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.logger_config import logger

load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")

DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}")

SYNC_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"

engine = create_async_engine(DATABASE_URL, connect_args={
        "ssl": False
    }
)


async def check_connection():
    try:
        async with engine.connect() as conn:
            logger.info("Соединение установлено")
    except Exception as e:
        logger.info(f"Ошибка подключения: {e}")