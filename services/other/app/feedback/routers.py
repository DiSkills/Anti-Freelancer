from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.feedback import views
from app.feedback.schemas import CreateFeedback
from app.permission import is_active
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
    db: AsyncSession = Depends(get_db)
):
    return await views.create_feedback(db, user_id, schema)
