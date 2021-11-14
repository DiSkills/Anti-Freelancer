from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.payments import views
from app.payments.schemas import URL
from app.views import is_active
from db import get_db

payments_router = APIRouter()


@payments_router.get(
    '/pay',
    name='Buy level',
    description='Buy level',
    response_description='URL',
    status_code=status.HTTP_201_CREATED,
    response_model=URL,
    tags=['payments'],
)
async def pay(amount: int, user: User = Depends(is_active), db: AsyncSession = Depends(get_db)):
    return await views.pay(db, user, amount)
