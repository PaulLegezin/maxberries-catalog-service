from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from app.schemas.product import ProductResponse, ProductsResponse, ProductCreate
from app.models.product import Product
from app.api.dependencies import get_db
from app.core.logger_config import logger


router = APIRouter(prefix="/products", tags=["products"])



@router.get("/products/{product_id}", response_model=ProductResponse)
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



@router.get("/products/", response_model=ProductsResponse)
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



@router.post("/products/", response_model=ProductResponse)
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
    


@router.put("/products/{id}", response_model=ProductResponse)
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
    


@router.delete("/products/{id}", status_code=204)
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
        
