import datetime
import typing

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import sub_category_crud, job_crud
from app.jobs.schemas import CreateJob


async def create_job(db: AsyncSession, schema: CreateJob) -> dict[str, typing.Any]:
    """
        Create job
        :param db: DB
        :type db: AsyncSession
        :param schema: Job data
        :type schema: CreateJob
        :return: New job
        :rtype: dict
        :raise HTTPException 400: Category not found
    """

    if not await sub_category_crud.exist(db, id=schema.category_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category not found')

    job = await job_crud.create(
        db,
        **{**schema.dict(), 'order_date': datetime.datetime.utcfromtimestamp(schema.order_date.timestamp())},
    )
    return job.__dict__
