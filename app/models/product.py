import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from app.models.category import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[Decimal] = mapped_column(nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
