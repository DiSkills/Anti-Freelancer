from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin import views
from app.admin.schemas import UsersPaginate, UserMaximal, RegisterAdmin, UpdateUser
from app.schemas import Message
from app.views import is_superuser
from db import get_db

admin_router = APIRouter()


@admin_router.get(
    '/users',
    name='Users admin',
    description='Users admin',
    response_description='Users',
    status_code=status.HTTP_200_OK,
    response_model=UsersPaginate,
    tags=['admin'],
    dependencies=[Depends(is_superuser)],
)
async def get_all_users(
        page: int = Query(default=1, gt=0),
        page_size: int = Query(default=1, gt=0),
        db: AsyncSession = Depends(get_db),
):
    return await views.get_all_users(db=db, page=page, page_size=page_size)


@admin_router.get(
    '/user/{user_id}',
    name='Get user',
    description='Get user',
    response_description='User',
    status_code=status.HTTP_200_OK,
    response_model=UserMaximal,
    tags=['admin'],
    dependencies=[Depends(is_superuser)],
)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await views.get_user(db, user_id)


@admin_router.post(
    '/user',
    name='Create user',
    description='Create user',
    response_description='New user',
    status_code=status.HTTP_201_CREATED,
    response_model=Message,
    tags=['admin'],
    dependencies=[Depends(is_superuser)],
)
async def create_user(schema: RegisterAdmin, db: AsyncSession = Depends(get_db)):
    return await views.create_user(db, schema)


@admin_router.put(
    '/user/{user_id}',
    name='Update user',
    description='Update user',
    response_description='User',
    status_code=status.HTTP_200_OK,
    response_model=UserMaximal,
    tags=['admin'],
    dependencies=[Depends(is_superuser)],
)
async def update_user(user_id: int, schema: UpdateUser, db: AsyncSession = Depends(get_db)):
    return await views.update_user(db, schema, user_id)


@admin_router.delete(
    '/github/unbind/{pk}',
    name='Unbind GitHub',
    description='Unbind GitHub',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    tags=['admin'],
    dependencies=[Depends(is_superuser)],
)
async def unbind_github(pk: int, db: AsyncSession = Depends(get_db)):
    return await views.unbind_github(db, pk)
