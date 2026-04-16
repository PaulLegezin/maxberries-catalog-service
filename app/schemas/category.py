import uuid
from datetime import datetime

from pydantic import BaseModel, Field

MIN_NAME_LENGTH = 1


class CategoryBase(BaseModel):
    name: str = Field(min_length=MIN_NAME_LENGTH)


class CategoryResponse(CategoryBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class CategoriesResponse(BaseModel):
    categories: list[CategoryResponse]


class CategoryCreate(CategoryBase):
    pass
