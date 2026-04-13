import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from app.repositories.product import ProductRepository
from app.schemas.product import ProductResponse, ProductsResponse, ProductCreate
from app.models.product import Product
from app.api.dependencies import get_db
from app.core.logger_config import logger


router = APIRouter(prefix="/products", tags=["products"])



@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ProductResponse:
    logger.info("Запрос на получение товара. ID: %s", product_id)
    repo = ProductRepository(db)

    try:
        product = await repo.get(product_id)
        
        if not product:
            logger.warning("Товар с ID: %s не найден", product_id)
            raise HTTPException(
                status_code=404, 
                detail="Товар не найден"
                )
        
        logger.info("Товар с ID: %s успешно отправлен клиенту", product_id)
        return product
    
    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Ошибка базы данных при поиске товара: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
            )



@router.get("/", response_model=ProductsResponse)
async def get_products(db: AsyncSession = Depends(get_db)) -> ProductsResponse:
    logger.info("Запрос на получение всех товаров")
    repo = ProductRepository(db)

    try:
        products = await repo.get_all()

        logger.info("Успешно найдено товаров: %s", len(products))
        return {"products": products}

    except Exception as e:
        logger.exception("Ошибка базы данных при поиске товаров: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
            )
    


@router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    logger.info("Запрос на создание товара: %s", product.name)
    repo = ProductRepository(db)

    try:   
        new_product = await repo.create(product.model_dump())

        logger.info("Товар успешно создан. ID: %s", new_product.id)
        return new_product
    
    except IntegrityError as e:
        logger.warning("Конфликт при создании товара: %s", str(e))
        raise HTTPException(
            status_code=400,
            detail="Товар с таким именем уже существует"
        )
    except Exception as e:
        logger.exception("Непредвиденная ошибка при создании товара")
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
        )
    


@router.put("/{id}", response_model=ProductResponse)
async def update_product(id: uuid.UUID, product: ProductCreate, db: AsyncSession = Depends(get_db)):
    logger.info("Запрос на обновление товара. ID: %s", id)
    repo = ProductRepository(db)

    try:
        new_product = await repo.update(id, product.model_dump())

        if not new_product:
            logger.warning("Товар не найден")
            raise HTTPException(
                status_code=404, 
                detail="Товар не найден"
                )
    
        logger.info("Товар ID успешно обновлен. ID: %s", id)
        return new_product

    except HTTPException:
        raise

    except IntegrityError as e:
        logger.warning("Ошибка целостности при обновлении товара %s: %s", id, str(e))
        raise HTTPException(
            status_code=400, 
            detail="Некорректные данные: проверьте ID категории или уникальность полей"
            )

    except Exception as e:
        logger.exception("Ошибка базы данных при поиске товара: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
            )
    


@router.delete("/{id}", status_code=204)
async def delete_product(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    logger.info("Запрос на удаление товара. ID: %s", id)
    repo = ProductRepository(db)

    try:
        del_prod = await repo.delete(id)

        if not del_prod:
            logger.warning("Товар не найден")
            raise HTTPException(
                status_code=404, 
                detail="Товар не найден"
                )
    
        logger.info("Товар успешно удален. ID: %s", id)

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Ошибка базы данных при удалении товара: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
            )
        
