import uuid

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Category]:
        stmt = select(Category)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, data: dict) -> Category:
        try:
            stmt = insert(Category).values(**data).returning(Category)
            result = await self.session.execute(stmt)
            new_category = result.scalar_one()

            await self.session.commit()
            await self.session.refresh(new_category)
            return new_category

        except IntegrityError:
            await self.session.rollback()
            raise

    async def update(self, cat_id: uuid.UUID, data: dict) -> Category | None:
        try:
            stmt = (
                update(Category)
                .where(Category.id == cat_id)
                .values(**data)
                .returning(Category)
            )
            result = await self.session.execute(stmt)
            new_category = result.scalar_one_or_none()
            if new_category:
                await self.session.commit()
                await self.session.refresh(new_category)
            return new_category
        except IntegrityError:
            raise

    async def delete(self, cat_id: uuid.UUID) -> bool:
        try:
            stmt = delete(Category).where(Category.id == cat_id).returning(Category.id)
            result = await self.session.execute(stmt)
            deleted_id = result.scalar_one_or_none()
            if deleted_id:
                await self.session.commit()
                return True
            return False
        except IntegrityError:
            await self.session.rollback()
            raise
