from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, join, func, or_
from sqlalchemy.orm import Session
from typing import Optional

from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.models.reviews import Review as ReviewModel
from app.schemas import Review as ReviewSchema, ReviewCreate
from app.db_depends import get_db

from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db
from app.models.users import User as UserModel
from app.auth import get_current_buyer


# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)


@router.get("/", response_model=list[ReviewSchema])
async def get_all_rewviews(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех отзывов.
    """
    result = await db.scalars(select(ReviewModel).where(ReviewModel.is_active == True))
    return result.all()


@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_buyer)
):
    """
    Создаёт новый отзыв, привязанный к текущему покупателю (только для 'buyer').
    """
    product_result = await db.scalars(
        select(ProductModel).where(ProductModel.id == review.product_id, ProductModel.is_active == True)
    )
    if not product_result.first():
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    review_result = await db.scalars(
        select(ReviewModel).where(ReviewModel.user_id == current_user.id, ReviewModel.is_active == True)
    )

    if review_result.first():
        raise HTTPException(status_code=409, detail="You already have review for this product")

    if review.grade < 1 or review.grade > 5:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

    db_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(db_review)
    await db.commit()

    # Вычисляем средний рейтинг всех активных отзывов для этого продукта
    rating_avg = await db.scalar(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == review.product_id,
            ReviewModel.is_active == True
        )
    )

    rating_value = int(round(rating_avg)) if rating_avg is not None else None
    
    # Обновляем рейтинг продукта
    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == review.product_id)
        .values(rating=rating_value)
    )
    await db.commit()

    await db.refresh(db_review)  # Для получения id и is_active из базы
    return db_review



@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_buyer)):
    """
    Выполняет мягкое удаление товара, если он принадлежит текущему продавцу (только для 'seller').
    """
    review_result = await db.scalars(select(ReviewModel).where(ReviewModel.id == review_id,
                                                             ReviewModel.is_active == True))
    review = review_result.first()
    if not review:
        raise HTTPException(status_code=404,detail="Review not found or inactive")


    user_result = await db.scalars(select(ReviewModel).where(ReviewModel.id == review_id, ReviewModel.is_active == True)
                                                      .where(or_(ReviewModel.user_id == current_user.id, current_user.role == 'admin')))
    user = user_result.first()
    if not user:
        raise HTTPException(status_code=403, detail="You can only update your own reviews")

    await db.execute(
        update(ReviewModel).where(ReviewModel.id == review_id).values(is_active=False)
    )
    await db.commit()
    await db.refresh(review)

    # Вычисляем средний рейтинг всех активных отзывов для этого продукта
    rating_avg = await db.scalar(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == review.product_id,
            ReviewModel.is_active == True
        )
    )

    rating_value = int(round(rating_avg)) if rating_avg is not None else None

    # Обновляем рейтинг продукта
    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == review.product_id)
        .values(rating=rating_value)
    )
    await db.commit()

    return {"message": "Review deleted"}
