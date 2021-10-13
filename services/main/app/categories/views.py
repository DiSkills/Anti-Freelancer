import typing

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.schemas import CreateCategory, UpdateCategory
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


async def get_super_category(db: AsyncSession, pk: int) -> dict[str, typing.Any]:
    """
        Get super category
        :param db: DB
        :type db: AsyncSession
        :param pk: Super category ID
        :type pk: int
        :return: Super category
        :rtype: dict
        :raise HTTPException 400: Super category not found
    """

    if not await super_category_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Super category not found')

    category = await super_category_crud.get(db, id=pk)
    return {
        **category.__dict__,
        'sub_categories': (
            sub_category.__dict__ for sub_category in category.sub_categories
        ),
    }


async def update_super_category(db: AsyncSession, schema: UpdateCategory, pk: int) -> dict[str, typing.Any]:
    """
        Update super category
        :param db: DB
        :type db: AsyncSession
        :param schema: New data
        :type schema: UpdateCategory
        :param pk: Super category ID
        :type pk: int
        :return: Super category
        :rtype: dict
        :raise HTTPException 400: Super category not found
    """

    if not await super_category_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Super category not found')

    category = await super_category_crud.update(db, {'id': pk}, **schema.dict())
    return {
        **category.__dict__,
        'sub_categories': (
            sub_category.__dict__ for sub_category in category.sub_categories
        ),
    }


async def delete_super_category(db: AsyncSession, pk: int) -> dict[str, str]:
    """
        Delete super category
        :param db: DB
        :type db: AsyncSession
        :param pk: Super category ID
        :type pk: int
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Super category not found
    """

    if not await super_category_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Super category not found')

    await super_category_crud.remove(db, id=pk)
    return {'msg': 'Super category has been deleted'}


async def get_sub_category(db: AsyncSession, pk: int) -> dict[str, typing.Union[str, int]]:
    """
        Get sub category
        :param db: DB
        :type db: AsyncSession
        :param pk: Sub category ID
        :type pk: int
        :return: Sub category
        :rtype: dict
        :raise HTTPException 400: Sub category not found
    """

    if not await sub_category_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Sub category not found')

    category = await sub_category_crud.get(db, id=pk)
    return category.__dict__


async def update_sub_category(db: AsyncSession, schema: UpdateCategory, pk: int) -> dict[str, typing.Union[str, int]]:
    """
        Update sub category
        :param db: DB
        :type db: AsyncSession
        :param schema: Schema
        :type schema: UpdateCategory
        :param pk: Sub category ID
        :type pk: int
        :return: Sub category
        :rtype: dict
        :raise HTTPException 400: Sub category not found
    """

    if not await sub_category_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Sub category not found')

    category = await sub_category_crud.update(db, {'id': pk}, **schema.dict())
    return category.__dict__


async def delete_sub_category(db: AsyncSession, pk: int) -> dict[str, str]:
    """
        Delete sub category
        :param db: DB
        :type db: AsyncSession
        :param pk: Sub category ID
        :type pk: int
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Sub category not found
    """

    if not await sub_category_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Sub category not found')

    await sub_category_crud.remove(db, id=pk)
    return {'msg': 'Sub category has been deleted'}
