from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.logger_config import logger

engine = create_async_engine(settings.database_url_async)


async def check_connection():
    try:
        async with engine.connect():
            logger.info("Соединение установлено")
    except Exception:
        logger.exception("Ошибка подключения")
        raise
