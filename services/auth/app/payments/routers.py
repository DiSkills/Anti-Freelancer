from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.payments import views
from app.payments.schemas import GetPayment
from app.schemas import Message
from app.views import is_freelancer
from db import get_db

payments_router = APIRouter()


@payments_router.get(
    '/pay',
    name='Buy level',
    description='Buy level',
    response_description='Payment',
    status_code=status.HTTP_201_CREATED,
    response_model=GetPayment,
    tags=['payments'],
)
async def pay(amount: int, user: User = Depends(is_freelancer), db: AsyncSession = Depends(get_db)):
    return await views.pay(db, user, amount)


@payments_router.get(
    '/check',
    name='Check payment',
    description='Check payment',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['payments'],
)
async def check(pk: int, db: AsyncSession = Depends(get_db)):
    return await views.check(db, pk)
