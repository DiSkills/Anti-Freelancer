from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.feedback import views
from app.feedback.schemas import CreateFeedback, GetFeedback, PaginateFeedbacks, UpdateFeedback
from app.permission import is_active, is_superuser
from app.schemas import Message
from db import get_db

feedbacks_router = APIRouter()


@feedbacks_router.post(
    '/',
    name='Create feedback',
    description='Create feedback',
    response_description='Message',
    response_model=Message,
    status_code=status.HTTP_201_CREATED,
    tags=['feedbacks'],
)
async def create_feedback(
    schema: CreateFeedback,
    user_id: int = Depends(is_active),
    db: AsyncSession = Depends(get_db),
):
    return await views.create_feedback(db, user_id, schema)


@feedbacks_router.get(
    '/',
    name='Get all feedbacks',
    description='Get all feedbacks',
    response_description='Feedbacks',
    response_model=PaginateFeedbacks,
    status_code=status.HTTP_200_OK,
    tags=['feedbacks'],
    dependencies=[Depends(is_superuser)],
)
async def get_all_feedbacks(
    page: int = Query(default=1, gt=0),
    page_size: int = Query(default=1, gt=0),
    db: AsyncSession = Depends(get_db),
):
    return await views.get_all_feedbacks(db=db, page=page, page_size=page_size)


@feedbacks_router.get(
    '/sort',
    name='Sort feedbacks',
    description='Sort feedbacks',
    response_description='Feedbacks',
    response_model=PaginateFeedbacks,
    status_code=status.HTTP_200_OK,
    tags=['feedbacks'],
    dependencies=[Depends(is_superuser)],
)
async def sort_feedbacks(
    desc: bool,
    page: int = Query(default=1, gt=0),
    page_size: int = Query(default=1, gt=0),
    db: AsyncSession = Depends(get_db),
):
    return await views.sort_feedbacks(db=db, page=page, page_size=page_size, desc=desc)


@feedbacks_router.get(
    '/{pk}',
    name='Get feedback',
    description='Get feedback',
    response_description='Feedback',
    response_model=GetFeedback,
    status_code=status.HTTP_200_OK,
    tags=['feedbacks'],
    dependencies=[Depends(is_superuser)],
)
async def get_feedback(pk: int, db: AsyncSession = Depends(get_db)):
    return await views.get_feedback(db, pk)


@feedbacks_router.put(
    '/{pk}',
    name='Update feedback',
    description='Update feedback',
    response_description='Feedback',
    response_model=GetFeedback,
    status_code=status.HTTP_200_OK,
    tags=['feedbacks'],
    dependencies=[Depends(is_superuser)],
)
async def update_feedback(pk: int, schema: UpdateFeedback, db: AsyncSession = Depends(get_db)):
    return await views.update_feedback(db, pk, schema)


@feedbacks_router.delete(
    '/{pk}',
    name='Delete feedback',
    description='Delete feedback',
    response_description='Message',
    response_model=Message,
    status_code=status.HTTP_200_OK,
    tags=['feedbacks'],
    dependencies=[Depends(is_superuser)],
)
async def delete_feedback(pk: int, db: AsyncSession = Depends(get_db)):
    return await views.delete_feedback(db, pk)
