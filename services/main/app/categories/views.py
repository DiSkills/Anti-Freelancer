import typing

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.schemas import CreateCategory
from app.crud import super_category_crud, sub_category_crud


async def create_category(db: AsyncSession, schema: CreateCategory) -> dict[str, typing.Union[str, int]]:
    """
        Create category (super and sub)
        :param db: DB
        :type db: AsyncSession
        :param schema: Category data
        :type schema: CreateCategory
        :return: New category data
        :rtype: dict
        :raise HTTPException 400: Super category not found
    """

    if schema.super_category_id:
        if not await super_category_crud.exist(db, id=schema.super_category_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Super category not found')
        category = await sub_category_crud.create(db, **schema.dict())
    else:
        del schema.super_category_id
        category = await super_category_crud.create(db, **schema.dict())
    return category.__dict__


async def get_categories(db: AsyncSession):
    """
        Get all categories
        :param db: DB
        :type db: AsyncSession
        :return: Categories
    """

    return (
        {
            **category.__dict__,
            'sub_categories': (
                sub_category.__dict__ for sub_category in category.sub_categories
            ),
        } for category in await super_category_crud.all(db, limit=1000)
    )
