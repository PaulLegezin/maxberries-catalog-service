from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime

class ProductResponse(BaseModel):
    id: int
    name: str = Field(min_length=1)
    price: Decimal = Field(ge=0)
    category_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProductsResponse(BaseModel):
    products: list[ProductResponse]


class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    price: Decimal = Field(ge=0)
    category_id: int
    description: str