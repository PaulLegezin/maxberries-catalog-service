import uuid
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime

MIN_NAME_LENGTH = 1
MIN_PRICE = 0

class ProductBase(BaseModel):
    name: str = Field(min_length=MIN_NAME_LENGTH)
    price: Decimal = Field(ge=MIN_PRICE)
    category_id: uuid.UUID
    description: str | None = None 

class ProductResponse(ProductBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ProductsResponse(BaseModel):
    products: list[ProductResponse]


class ProductCreate(ProductBase):
    pass