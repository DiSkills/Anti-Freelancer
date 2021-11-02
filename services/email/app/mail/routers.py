from fastapi import APIRouter, status

from app.mail import views
from app.mail.schemas import SendData
from app.schemas import Message

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
async def send(schema: SendData):
    return await views.send(schema)
