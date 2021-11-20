from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.permission import is_active, is_superuser
from app.review import views
from app.review.schemas import CreateReview, GetReview, ReviewPaginate, UpdateReview
from db import get_db

review_router = APIRouter()
SORTING_DESCRIPTION = '''
asc - sorting by ID; desc - sorting by -ID; asc_appraisal - sorting by appraisal; desc_appraisal - sorting by -appraisal
'''


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
    sort: str = Query(default='desc', description=SORTING_DESCRIPTION),
    page: int = Query(default=1, gt=0),
    page_size: int = Query(default=1, gt=0),
    db: AsyncSession = Depends(get_db),
):
    return await views.get_all_reviews(db=db, page=page, page_size=page_size, sort=sort)


@review_router.get(
    '/{pk}',
    name='Get review',
    description='Get review',
    response_description='Review',
    status_code=status.HTTP_200_OK,
    response_model=GetReview,
    tags=['reviews'],
)
async def get_review(pk: int, db: AsyncSession = Depends(get_db)):
    return await views.get_review(db, pk)


@review_router.put(
    '/admin/{pk}',
    name='Update review (admin)',
    description='Update review (admin)',
    response_description='Review',
    status_code=status.HTTP_200_OK,
    response_model=GetReview,
    tags=['admin'],
)
async def admin_update_review(
    pk: int,
    schema: UpdateReview,
    user_id: int = Depends(is_superuser),
    db: AsyncSession = Depends(get_db),
):
    return await views.update_review(db, pk, schema, user_id, True)


@review_router.put(
    '/{pk}',
    name='Update review',
    description='Update review',
    response_description='Review',
    status_code=status.HTTP_200_OK,
    response_model=GetReview,
    tags=['reviews'],
)
async def update_review(
    pk: int,
    schema: UpdateReview,
    user_id: int = Depends(is_active),
    db: AsyncSession = Depends(get_db),
):
    return await views.update_review(db, pk, schema, user_id)
