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
        query = await db.execute(sqlalchemy.exists(sqlalchemy.select(self.__model.id).filter_by(**kwargs)).select())
        return query.scalar()

    async def get(self, db: AsyncSession, **kwargs) -> typing.Optional[ModelType]:
        query = await db.execute(sqlalchemy.select(self.__model).filter_by(**kwargs))
        return query.scalars().first()

    async def create(self, db: AsyncSession, **kwargs) -> ModelType:
        instance = self.__model(**kwargs)
        db.add(instance)
        await db.flush()
        await db.commit()
        return instance

    async def update(self, db: AsyncSession, filter_by: dict, **kwargs) -> ModelType:
        query = sqlalchemy.update(self.__model).filter_by(**filter_by).values(**kwargs)
        query.execution_options(synchronize_session="fetch")
        await db.execute(query)
        await db.commit()
        return await self.get(db, **filter_by)

    async def remove(self, db: AsyncSession, **kwargs) -> None:
        await db.execute(sqlalchemy.delete(self.__model).filter_by(**kwargs))
        await db.commit()

    async def all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ModelType]:
        query = await db.execute(
            sqlalchemy.select(self.__model).order_by(self.__model.id.desc()).offset(skip).limit(limit)
        )
        return query.scalars().all()
