from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.notification import views
from app.notification.schemas import GetNotification
from app.permission import is_active
from app.schemas import Message
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


@notification_router.get(
    '/{pk}',
    name='Get notification',
    description='Get notification',
    response_description='Notification',
    status_code=status.HTTP_200_OK,
    response_model=GetNotification,
    tags=['notifications'],
)
async def get_notification(pk: int, user_id: int = Depends(is_active), db: AsyncSession = Depends(get_db)):
    return await views.get_notification(db, user_id, pk)


@notification_router.delete(
    '/',
    name='View notifications',
    description='View notifications',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['notifications'],
)
async def view_notifications(user_id: int = Depends(is_active), db: AsyncSession = Depends(get_db)):
    return await views.view_notifications(db, user_id)


@notification_router.delete(
    '/{pk}',
    name='View notification',
    description='View notification',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['notifications'],
)
async def view_notification(pk: int, user_id: int = Depends(is_active), db: AsyncSession = Depends(get_db)):
    return await views.view_notification(db, user_id, pk)
