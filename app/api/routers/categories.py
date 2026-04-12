from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from app.schemas.category import CategoriesResponse, CategoryResponse, CategoryCreate
from app.models.category import Category
from app.api.dependencies import get_db


from app.core.logger_config import logger


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/categories/", response_model=CategoriesResponse)
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



@router.post("/categories/", response_model=CategoryResponse)
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
    


@router.put("/categories/{id}", response_model=CategoryResponse)
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
    

    
@router.delete("/categories/{id}", status_code=204)
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