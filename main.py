import logging
import pythonjsonlogger.jsonlogger as jsonlogger
from fastapi import FastAPI, Depends, HTTPException
from schemas import (
    ProductResponse, ProductsResponse, 
    CategoriesResponse, ProductCreate, 
    CategoryResponse, CategoryCreate
    )
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, insert, update, delete
from contextlib import asynccontextmanager

from db import engine
from models import Product, Category
from db import check_connection

from prometheus_fastapi_instrumentator import Instrumentator

logger = logging.getLogger("fastapi_elk")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):

    await check_connection()
    yield

app = FastAPI(lifespan=lifespan)

Instrumentator().instrument(app).expose(app)

SessionLocal = async_sessionmaker(bind=engine)

async def get_db():
    async with SessionLocal() as db:
        yield db



@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)) -> ProductResponse:
    logger.info("Запрос на получение товара. ID: %s", product_id)

    try:
        stmt = select(Product).where(Product.id == product_id)
        result = await db.execute(stmt)
        product = result.scalar_one_or_none()

    except Exception as e:
        logger.exception("Ошибка базы данных при поиске товара: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
            )
    
    if product is None:
        logger.warning("Товар с ID: %s не найден", product_id)
        raise HTTPException(
            status_code=404, 
            detail="Товар не найден"
            )
    
    logger.info("Товар с ID: %s успешно отправлен клиенту", product_id)
    return product



@app.get("/products/", response_model=ProductsResponse)
async def get_products(db: AsyncSession = Depends(get_db)) -> ProductsResponse:
    logger.info("Запрос на получение всех товаров")

    try:
        stmt = select(Product)
        result = await db.execute(stmt)
        products = result.scalars().all()

    except Exception as e:
        logger.exception("Ошибка базы данных при поиске товаров: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
            )
    
    logger.info("Успешно найдено товаров: %s", len(products))
    return {"products": products}



@app.get("/categories/", response_model=CategoriesResponse)
async def get_categories(db: AsyncSession = Depends(get_db)) -> CategoriesResponse:
    logger.info("Запрос на получение всех категорий")

    try:
        stmt = select(Category)
        result = await db.execute(stmt)
        categories = result.scalars().all()

    except Exception as e:
        logger.exception("Ошибка базы данных при поиске категорий: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
            )
    
    logger.info("Успешно найдено категорий: %s", len(categories))
    return {"categories": categories}



@app.post("/products/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    logger.info("Запрос на создание товара: %s", product.name)

    try:   
        stmt = insert(Product).values(**product.model_dump()).returning(Product)
        result = await db.execute(stmt)
        new_product = result.scalar_one()

        await db.commit()
        await db.refresh(new_product)
        logger.info("Товар успешно создан. ID: %s", new_product.id)
        return new_product
    
    except IntegrityError as e:
        await db.rollback()
        logger.warning("Конфликт при создании товара: %s", str(e))
        raise HTTPException(
            status_code=400,
            detail="Товар с таким именем уже существует"
        )
    except Exception as e:
        await db.rollback()
        logger.exception("Непредвиденная ошибка при создании товара")
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
        )



@app.post("/categories/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_db)):
    logger.info("Запрос на создание категории: %s", category.name)

    try:
        stmt = insert(Category).values(**category.model_dump()).returning(Category)
        result = await db.execute(stmt)
        new_category = result.scalar_one()
        
        await db.commit()
        await db.refresh(new_category) 
        logger.info("Категория успешно создана. ID: %s", new_category.id)
        return new_category

    except IntegrityError as e:
        await db.rollback()
        logger.warning("Конфликт при создании категории: %s", str(e))
        raise HTTPException(
            status_code=400, 
            detail="Категория с таким именем уже существует"
        )
        
    except Exception as e:
        await db.rollback()
        logger.exception("Непредвиденная ошибка при создании категории", )
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
        )



@app.put("/products/{id}", response_model=ProductResponse)
async def update_product(id: int, product: ProductCreate, db: AsyncSession = Depends(get_db)):
    logger.info("Запрос на обновление товара. ID: %s", id)

    try:
        stmt = update(Product).where(Product.id == id).values(**product.model_dump()).returning(Product)
        result = await db.execute(stmt)
        new_product = result.scalar_one_or_none()

        if not new_product:
            logger.warning("Товар не найден")
            raise HTTPException(
                status_code=404, 
                detail="Товар не найден"
                )
    
        await db.commit()
        await db.refresh(new_product)
        logger.info("Товар ID успешно обновлен. ID: %s", id)
        return new_product

    except HTTPException:
        raise

    except Exception as e:
        await db.rollback()
        logger.exception("Ошибка базы данных при поиске товара: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
            )
    



@app.put("/categories/{id}", response_model=CategoryResponse)
async def update_category(id: int, category: CategoryCreate, db: AsyncSession = Depends(get_db)):
    logger.info("Запрос на обновление категории. ID: %s", id)
        
    try:    
        stmt = update(Category).where(Category.id == id).values(**category.model_dump()).returning(Category)
        result = await db.execute(stmt)
        new_category = result.scalar_one_or_none()

        if not new_category:
            logger.warning("Категория не найдена")
            raise HTTPException(
                status_code=404, 
                detail="Категория не найдена"
                )
    
        await db.commit()
        await db.refresh(new_category)
        logger.info("Категория успешно обновлена. ID: %s", id)
        return new_category
    
    except HTTPException:
        raise

    except Exception as e:
        await db.rollback()
        logger.exception("Ошибка базы данных при поиске категории: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
            )
    



@app.delete("/products/{id}", status_code=204)
async def delete_product(id: int, db: AsyncSession = Depends(get_db)):
    logger.info("Запрос на удаление товара. ID: %s", id)

    try:
        stmt = delete(Product).where(Product.id == id).returning(Product.id)
        result = await db.execute(stmt)
        deleted_id = result.scalar_one_or_none()

        if not deleted_id:
            logger.warning("Товар не найден")
            raise HTTPException(
                status_code=404, 
                detail="Товар не найден"
                )
    
        await db.commit()
        logger.info("Товар успешно удален. ID: %s", id)

    except HTTPException:
        raise

    except Exception as e:
        await db.rollback()
        logger.exception("Ошибка базы данных при удалении товара: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
            )



@app.delete("/categories/{id}", status_code=204)
async def delete_category(id: int, db: AsyncSession = Depends(get_db)):
    logger.info("Запрос на удаление категории. ID: %s", id)

    try:
        stmt = delete(Category).where(Category.id == id).returning(Category.id)
        result = await db.execute(stmt)
        deleted_id = result.scalar_one_or_none()

        if not deleted_id:
            logger.warning("Категория не найдена")
            raise HTTPException(
                status_code=404, 
                detail="Категория не найдена"
                )
        
        await db.commit()
        logger.info("Категория успешно удалена. ID: %s", id)

    except IntegrityError:
        await db.rollback()
        logger.warning("Попытка удаления категории ID: %s, которая используется в товарах", id)
        raise HTTPException(
            status_code=400, 
            detail="Нельзя удалить категорию, пока в ней есть товары"
        )
    except Exception:
        await db.rollback()
        logger.exception("Критическая ошибка при удалении категории ID: %s", id)
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
            )