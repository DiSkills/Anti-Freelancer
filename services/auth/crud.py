import typing

import sqlalchemy
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db import Base

ModelType = typing.TypeVar('ModelType', bound=Base)
CreateSchemaType = typing.TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = typing.TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUD(typing.Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """ CRUD """

    def __init__(self, model: typing.Type[ModelType]) -> None:
        self.__model = model

    async def exist(self, db: AsyncSession, **kwargs) -> bool:
        """
            Exist
            :param db: DB
            :type db: AsyncSession
            :param kwargs: kwargs
            :return: Exist instance?
            :rtype: bool
        """
        query = await db.execute(sqlalchemy.exists(sqlalchemy.select(self.__model.id).filter_by(**kwargs)).select())
        return query.scalar()

    async def get(self, db: AsyncSession, **kwargs) -> typing.Optional[ModelType]:
        """
            Get
            :param db: DB
            :type db: AsyncSession
            :param kwargs: kwargs
            :return: Instance
        """
        query = await db.execute(sqlalchemy.select(self.__model).filter_by(**kwargs))
        return query.scalars().first()

    async def create(self, db: AsyncSession, **kwargs) -> ModelType:
        """
            Create instance
            :param db: DB
            :type db: AsyncSession
            :param kwargs: kwargs
            :return: New instance
        """
        instance = self.__model(**kwargs)
        db.add(instance)
        await db.flush()
        await db.commit()
        return instance

    async def update(self, db: AsyncSession, filter_by: dict, **kwargs) -> ModelType:
        """
            Update instance
            :param db: DB
            :type db: AsyncSession
            :param filter_by: Filter by
            :type filter_by: dict
            :param kwargs: kwargs
            :return: Instance
        """
        query = sqlalchemy.update(self.__model).filter_by(**filter_by).values(**kwargs)
        query.execution_options(synchronize_session="fetch")
        await db.execute(query)
        await db.commit()
        return await self.get(db, **filter_by)

    async def remove(self, db: AsyncSession, **kwargs) -> None:
        """
            Remove instance
            :param db: DB
            :type db: AsyncSession
            :param kwargs: kwargs
            :return: None
        """
        await db.execute(sqlalchemy.delete(self.__model).filter_by(**kwargs))
        await db.commit()

    async def all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """
            All
            :param db: DB
            :type db: AsyncSession
            :param skip: Skip
            :type self: int
            :param limit: Limit
            :type limit: int
            :return: Instances
            :rtype: list
        """
        query = await db.execute(
            sqlalchemy.select(self.__model).order_by(self.__model.id.desc()).offset(skip).limit(limit)
        )
        return query.scalars().all()
