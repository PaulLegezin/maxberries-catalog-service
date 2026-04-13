import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category import CategoryRepository
from app.schemas.category import CategoriesResponse, CategoryResponse, CategoryCreate
from app.api.dependencies import get_db


from app.core.logger_config import logger


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=CategoriesResponse)
async def get_categories(db: AsyncSession = Depends(get_db)) -> CategoriesResponse:
    logger.info("Запрос на получение всех категорий")
    repo = CategoryRepository(db)

    try:
        categories = await repo.get_all()

    except Exception as e:
        logger.exception("Ошибка базы данных при поиске категорий: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
            )
    
    logger.info("Успешно найдено категорий: %s", len(categories))
    return {"categories": categories}



@router.post("/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_db)):
    logger.info("Запрос на создание категории: %s", category.name)
    repo = CategoryRepository(db)

    try:
        new_category = await repo.create(category.model_dump())
        
        logger.info("Категория успешно создана. ID: %s", new_category.id)
        return new_category

    except IntegrityError as e:
        logger.warning("Конфликт при создании категории: %s", str(e))
        raise HTTPException(
            status_code=400, 
            detail="Категория с таким именем уже существует"
        )
        
    except Exception as e:
        logger.exception("Непредвиденная ошибка при создании категории", )
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
        )
    


@router.put("/{id}", response_model=CategoryResponse)
async def update_category(id: uuid.UUID, category: CategoryCreate, db: AsyncSession = Depends(get_db)):
    logger.info("Запрос на обновление категории. ID: %s", id)
    repo = CategoryRepository(db)
        
    try:    
        new_category = await repo.update(id, category.model_dump())
        if not new_category:
            logger.warning("Категория ID %s не найдена для обновления", id)
            raise HTTPException(status_code=404, detail="Категория не найдена")
        
        logger.info("Категория ID %s успешно обновлена", id)
        return new_category
    
    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Ошибка базы данных при поиске категории: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
            )
    

    
@router.delete("/{id}", status_code=204)
async def delete_category(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    logger.info("Запрос на удаление категории. ID: %s", id)
    repo = CategoryRepository(db)

    try:
        del_cat = await repo.delete(id)

        if not del_cat:
            logger.warning("Категория не найдена")
            raise HTTPException(
                status_code=404, 
                detail="Категория не найдена"
                )
        
        logger.info("Категория успешно удалена. ID: %s", id)

    except IntegrityError:
        logger.warning("Попытка удаления категории ID: %s, которая используется в товарах", id)
        raise HTTPException(
            status_code=400, 
            detail="Нельзя удалить категорию, пока в ней есть товары"
        )
    except Exception:
        logger.exception("Критическая ошибка при удалении категории ID: %s", id)
        raise HTTPException(
            status_code=500, 
            detail="Внутренняя ошибка сервера"
            )