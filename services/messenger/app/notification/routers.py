from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.notification import views
from app.notification.schemas import GetNotification
from app.permission import is_active
from db import get_db

notification_router = APIRouter()


@notification_router.get(
    '/',
    name='Get notifications',
    description='Get notifications',
    response_description='Notifications',
    status_code=status.HTTP_200_OK,
    response_model=list[GetNotification],
    tags=['notifications'],
)
async def get_notifications(user_id: int = Depends(is_active), db: AsyncSession = Depends(get_db)):
    return await views.get_notifications(db, user_id)
