import datetime
import typing

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import sub_category_crud, job_crud
from app.jobs.schemas import CreateJob
from app.models import Job
from app.service import paginate
from config import SERVER_MAIN_BACKEND, API


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


@paginate(job_crud.all, job_crud.exist_page, f'{SERVER_MAIN_BACKEND}{API}/jobs/')
async def get_all_jobs(*, db: AsyncSession, page: int, page_size: int, queryset: list[Job]):
    """
        Get all jobs
        :param db: DB
        :type db: AsyncSession
        :param page: Page
        :type page: int
        :param page_size: Page size
        :type page_size: int
        :param queryset: Jobs
        :type queryset: list
        :return: Jobs
    """
    return (job.__dict__ for job in queryset)


@paginate(job_crud.all_for_category, job_crud.exist_page, f'{SERVER_MAIN_BACKEND}{API}/jobs/category', 'category_id')
async def get_all_jobs_for_category(
        *, db: AsyncSession, queryset: list[Job], page: int, page_size: int, category_id: int,
):
    """
        Get all for category
        :param db: DB
        :type db: AsyncSession
        :param queryset: Jobs
        :type queryset: list
        :param page: Page
        :type page: int
        :param page_size: Page size
        :type page_size: int
        :param category_id: Category ID
        :type category_id: int
        :return: Jobs
    """
    return (job.__dict__ for job in queryset)


@paginate(job_crud.search, job_crud.search_exist, f'{SERVER_MAIN_BACKEND}{API}/jobs/search', 'search')
async def search_jobs(*, db: AsyncSession, page: int, page_size: int, search: str, queryset: list[Job]):
    """
        Search jobs
        :param db: DB
        :type db: AsyncSession
        :param page: Page
        :type page: int
        :param page_size: Page size
        :type page_size: int
        :param search: Search
        :type search: str
        :param queryset: Jobs
        :type queryset: list
        :return: Jobs
    """
    return (job.__dict__ for job in queryset)
