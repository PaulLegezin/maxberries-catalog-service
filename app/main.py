from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routers import categories_router, products_router
from app.core.db import check_connection
from app.core.logger_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения...")
    await check_connection()
    yield
    logger.info("Остановка приложения...")


app = FastAPI(lifespan=lifespan, title="Maxberries Catalog Service")


app.include_router(products_router)
app.include_router(categories_router)


Instrumentator().instrument(app).expose(app)


@app.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok"}
