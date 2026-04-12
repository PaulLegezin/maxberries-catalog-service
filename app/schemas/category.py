from pydantic import BaseModel, Field
from datetime import datetime

class CategoryResponse(BaseModel):
    id: int
    name: str = Field(min_length=1)
    created_at: datetime

    class Config:
        from_attributes = True


class CategoriesResponse(BaseModel):
    categories: list[CategoryResponse]


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1)