from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.permission import is_active
from app.review import views
from app.review.schemas import CreateReview, GetReview
from db import get_db

review_router = APIRouter()


@review_router.post(
    '/',
    name='Create review',
    description='Create review',
    response_description='Review',
    status_code=status.HTTP_201_CREATED,
    response_model=GetReview,
    tags=['reviews'],
)
async def create_review(schema: CreateReview, user_id: int = Depends(is_active), db: AsyncSession = Depends(get_db)):
    return await views.create_review(db, user_id, schema)
