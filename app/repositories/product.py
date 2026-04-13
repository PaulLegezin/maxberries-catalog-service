import uuid
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.product import Product

class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: uuid.UUID) -> Product:
        stmt = select(Product).where(Product.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self) -> list[Product]:
        stmt = select(Product)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, data: dict) -> Product:
        try:   
            stmt = insert(Product).values(**data).returning(Product)
            result = await self.session.execute(stmt)
            new_product = result.scalar_one()

            await self.session.commit()
            await self.session.refresh(new_product)
            return new_product
        
        except IntegrityError as e:
            await self.session.rollback()
            raise 
            
    async def update(self, id: uuid.UUID, data: dict) -> Product | None:
        try:  
            stmt = update(Product).where(Product.id == id).values(**data).returning(Product)
            result = await self.session.execute(stmt)
            new_product = result.scalar_one_or_none()

            if new_product:
                await self.session.commit()
                await self.session.refresh(new_product)
            return new_product 
        except IntegrityError:
            await self.session.rollback()
            raise

    async def delete(self, id: uuid.UUID) -> bool:
        try:
            stmt = delete(Product).where(Product.id == id).returning(Product.id)
            result = await self.session.execute(stmt)
            deleted_id = result.scalar_one_or_none()

            if deleted_id:
                await self.session.commit()
                return True
            return False
        except IntegrityError:
            await self.session.rollback()
            raise
