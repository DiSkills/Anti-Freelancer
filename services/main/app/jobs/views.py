import datetime
import typing

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import requests
from app.crud import sub_category_crud, job_crud
from app.jobs.schemas import CreateJob, UpdateJob
from app.models import Job
from app.service import paginate, user_exist
from config import SERVER_MAIN_BACKEND, API


async def create_job(db: AsyncSession, schema: CreateJob, customer_id: int) -> dict[str, typing.Any]:
    """
        Create job
        :param db: DB
        :type db: AsyncSession
        :param schema: Job data
        :type schema: CreateJob
        :param customer_id: Customer ID
        :type customer_id: int
        :return: New job
        :rtype: dict
        :raise HTTPException 400: Category not found
    """

    if not await sub_category_crud.exist(db, id=schema.category_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category not found')

    job = await job_crud.create(
        db,
        **{**schema.dict(), 'order_date': datetime.datetime.utcfromtimestamp(schema.order_date.timestamp())},
        customer_id=customer_id,
    )
    return job.__dict__


@user_exist('pk', freelancer=True)
@paginate(
    job_crud.filter_jobs_for_freelancer,
    job_crud.exist_page_for_freelancer_jobs,
    f'{SERVER_MAIN_BACKEND}{API}/jobs/freelancer',
    'pk'
)
async def get_jobs_for_freelancer(*, db: AsyncSession, page: int, page_size: int, pk: int, queryset: list[Job]):
    """
        Get jobs for freelancer
        :param db: DB
        :type db: AsyncSession
        :param page: Page
        :type page: int
        :param page_size: Page size
        :type page_size: int
        :param pk: Freelancer ID
        :type pk: int
        :param queryset: Jobs
        :type queryset: list
        :return: Jobs
    """
    return (job.__dict__ for job in queryset)


@user_exist('pk', customer=True)
@paginate(
    job_crud.filter_jobs_for_customer,
    job_crud.exist_page_for_customer_jobs,
    f'{SERVER_MAIN_BACKEND}{API}/jobs/customer',
    'pk',
)
async def get_jobs_for_customer(*, db: AsyncSession, page: int, page_size: int, pk: int, queryset: list[Job]):
    """
        Get jobs for customer
        :param db: DB
        :type db: AsyncSession
        :param page: Page
        :type page: int
        :param page_size: Page size
        :type page_size: int
        :param pk: Customer ID
        :type pk: int
        :param queryset: Jobs
        :type queryset: list
        :return: Jobs
    """
    return (job.__dict__ for job in queryset)


@paginate(job_crud.all, job_crud.exist_page, f'{SERVER_MAIN_BACKEND}{API}/jobs/all')
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


@paginate(
    job_crud.all_for_category,
    job_crud.exist_page,
    f'{SERVER_MAIN_BACKEND}{API}/jobs/category/all',
    'category_id',
)
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


@paginate(job_crud.get_all_active_jobs, job_crud.exist_page_active_jobs, f'{SERVER_MAIN_BACKEND}{API}/jobs/')
async def get_all_jobs_without_completed(*, db: AsyncSession, page: int, page_size: int, queryset: list[Job]):
    """
        Get all jobs without completed
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


@paginate(
    job_crud.all_for_category_without_completed,
    job_crud.exist_page_active_jobs,
    f'{SERVER_MAIN_BACKEND}{API}/jobs/category', 'category_id'
)
async def get_all_jobs_without_completed_for_category(
        *, db: AsyncSession, queryset: list[Job], page: int, page_size: int, category_id: int,
):
    """
        Get all for category without completed
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


async def get_job(db: AsyncSession, pk: int) -> dict[str, typing.Any]:
    """
        Get job
        :param db: DB
        :type db: AsyncSession
        :param pk: Job ID
        :type pk: int
        :return: Job
        :rtype: dict
        :raise HTTPException 400: Job not found
    """

    if not await job_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Job not found')

    job = await job_crud.get(db, id=pk)
    return job.__dict__


async def select_executor(db: AsyncSession, pk: int, user_id: int, owner_id: int) -> dict:
    """
        Select executor
        :param db: DB
        :type db: AsyncSession
        :param pk: Job ID
        :type pk: int
        :param user_id: Executor ID
        :type user_id: int
        :param owner_id: Owner ID
        :type owner_id: int
        :return: Job
        :rtype: dict
        :raise HTTPException 400: Job not found
        :raise HTTPException 400: Job is completed
        :raise HTTPException 400: Executor already appointed
        :raise HTTPException 400: User not owner this job
        :raise HTTPException 400: User cannot fulfill your order
        :raise HTTPException 400: Executor not freelancer
    """

    if not await job_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Job not found')
    job = await job_crud.get(db, id=pk)

    if job.completed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Job is completed')

    if job.executor_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Executor already appointed')

    if job.customer_id != owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You not owner this job')

    if user_id == job.customer_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You cannot fulfill your job')

    executor_data: dict = await requests.get_user(user_id)

    if not executor_data['freelancer']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Executor not freelancer')

    job = await job_crud.update(db, {'id': pk}, executor_id=executor_data['id'])
    return job.__dict__


async def complete_job(db: AsyncSession, pk: int, user_id: int) -> dict[str, str]:
    """
        Complete job
        :param db: DB
        :type db: AsyncSession
        :param pk: Job ID
        :type pk: int
        :param user_id: Owner ID
        :type user_id: int
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Job not found
        :raise HTTPException 400: User not owner this job
        :raise HTTPException 400: Job already completed
        :raise HTTPException 400: Job has not executor
    """

    if not await job_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Job not found')
    job = await job_crud.get(db, id=pk)

    if job.customer_id != user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You not owner this job')

    if job.completed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Job already completed')

    if not job.executor_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Job has not executor')

    await job_crud.update(db, {'id': pk}, completed=True)
    return {'msg': 'Job has been completed'}


async def update_job(db: AsyncSession, pk: int, schema: UpdateJob, user_id: int) -> dict:
    """
        Update job
        :param db: DB
        :type db: AsyncSession
        :param pk: Job ID
        :type pk: int
        :param schema: New job data
        :type schema: UpdateJob
        :param user_id: User ID
        :type user_id: int
        :return: Job
        :rtype: dict
        :raise HTTPException 400: Job not found
        :raise HTTPException 400: User not owner this job
        :raise HTTPException 400: Job is completed
        :raise HTTPException 400: Category not found
    """

    if not await job_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Job not found')
    job = await job_crud.get(db, id=pk)

    if job.customer_id != user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You not owner this job')

    if job.completed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Job is completed')

    if not await sub_category_crud.exist(db, id=schema.category_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category not found')

    job = await job_crud.update(
        db,
        {'id': pk},
        **{**schema.dict(), 'order_date': datetime.datetime.utcfromtimestamp(schema.order_date.timestamp())}
    )
    return job.__dict__
