from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.mail import views
from app.mail.schemas import SendData
from app.schemas import Message
from db import get_db

mail_router = APIRouter()


@mail_router.post(
    '/send',
    name='Send email',
    description='Send email',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['email'],
)
async def send(schema: SendData, db: AsyncSession = Depends(get_db)):
    return await views.send(db, schema)
