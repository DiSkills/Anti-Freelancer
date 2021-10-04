from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import views
from app.schemas import Register, Message
from db import get_db

auth_router = APIRouter()


@auth_router.post(
    '/register',
    name='Register',
    description='Register user',
    response_description='Message',
    status_code=status.HTTP_201_CREATED,
    response_model=Message,
    tags=['auth'],
)
async def register(schema: Register, db: AsyncSession = Depends(get_db)):
    return await views.register(db, schema)


@auth_router.get(
    '/verify',
    name='Verification account',
    description='Verification user account',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['auth'],
)
async def verify(link: str, db: AsyncSession = Depends(get_db)):
    return await views.verify(db, link)
