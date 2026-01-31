from decimal import Decimal
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Boolean, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)  # New
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)  #

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    seller: Mapped["User"] = relationship("User", back_populates="products")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="product")

