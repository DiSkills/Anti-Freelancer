from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.permission import is_active
from app.review import views
from app.review.schemas import CreateReview, GetReview, ReviewPaginate
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


@review_router.get(
    '/',
    name='Get all',
    description='Get all',
    response_description='Reviews',
    status_code=status.HTTP_200_OK,
    response_model=ReviewPaginate,
    tags=['reviews'],
)
async def get_all_reviews(
    sort: str = Query(default='desc'),
    page: int = Query(default=1, gt=0),
    page_size: int = Query(default=1, gt=0),
    db: AsyncSession = Depends(get_db),
):
    return await views.get_all_reviews(db=db, page=page, page_size=page_size, sort=sort)