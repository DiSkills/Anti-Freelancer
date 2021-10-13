from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories import views
from app.categories.schemas import CreateCategory, GetCategory, GetSuperCategory, UpdateCategory
from app.permission import is_superuser
from db import get_db

categories_router = APIRouter()


@categories_router.post(
    '/',
    name='Create category',
    description='Create category',
    response_description='New category',
    status_code=status.HTTP_201_CREATED,
    response_model=GetCategory,
    tags=['categories'],
    dependencies=[Depends(is_superuser)],
)
async def create_category(schema: CreateCategory, db: AsyncSession = Depends(get_db)):
    return await views.create_category(db, schema)


@categories_router.get(
    '/',
    name='Get categories',
    description='Get categories',
    response_description='Categories',
    status_code=status.HTTP_200_OK,
    response_model=list[GetSuperCategory],
    tags=['categories'],
)
async def get_categories(db: AsyncSession = Depends(get_db)):
    return await views.get_categories(db)


@categories_router.get(
    '/sup/{pk}',
    name='Get super category',
    description='Get super category',
    response_description='Super category',
    status_code=status.HTTP_200_OK,
    response_model=GetSuperCategory,
    tags=['super-categories'],
)
async def get_super_category(pk: int, db: AsyncSession = Depends(get_db)):
    return await views.get_super_category(db, pk)


@categories_router.put(
    '/sup/{pk}',
    name='Update super category',
    description='Update super category',
    response_description='Super category',
    status_code=status.HTTP_200_OK,
    response_model=GetSuperCategory,
    tags=['super-categories'],
    dependencies=[Depends(is_superuser)],
)
async def update_super_category(pk: int, schema: UpdateCategory, db: AsyncSession = Depends(get_db)):
    return await views.update_super_category(db, schema, pk)


@categories_router.get(
    '/sub/{pk}',
    name='Get sub category',
    description='Get sub category',
    response_description='Sub category',
    status_code=status.HTTP_200_OK,
    response_model=GetCategory,
    tags=['sub-categories'],
)
async def get_sub_category(pk: int, db: AsyncSession = Depends(get_db)):
    return await views.get_sub_category(db, pk)


@categories_router.put(
    '/sub/{pk}',
    name='Update sub category',
    description='Update sub category',
    response_description='Sub category',
    status_code=status.HTTP_200_OK,
    response_model=GetCategory,
    tags=['sub-categories'],
    dependencies=[Depends(is_superuser)],
)
async def update_sub_category(pk: int, schema: UpdateCategory, db: AsyncSession = Depends(get_db)):
    return await views.update_sub_category(db, schema, pk)
