from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.jobs import views
from app.jobs.schemas import CreateJob, GetJob, JobsPaginate
from app.permission import is_customer
from db import get_db

jobs_router = APIRouter()


@jobs_router.post(
    '/',
    name='Create job',
    description='Create job',
    response_description='Job',
    status_code=status.HTTP_201_CREATED,
    response_model=GetJob,
    tags=['jobs'],
)
async def create_job(schema: CreateJob, customer_id: int = Depends(is_customer), db: AsyncSession = Depends(get_db)):
    return await views.create_job(db, schema, customer_id)


@jobs_router.get(
    '/',
    name='Get all jobs',
    description='Get all jobs',
    response_description='Jobs',
    status_code=status.HTTP_200_OK,
    response_model=JobsPaginate,
    tags=['jobs'],
)
async def get_all_jobs(
        page: int = Query(default=1, gt=0),
        page_size: int = Query(default=1, gt=0),
        db: AsyncSession = Depends(get_db)
):
    return await views.get_all_jobs(db=db, page=page, page_size=page_size)


@jobs_router.get(
    '/category',
    name='Get all jobs for category',
    description='Get all jobs for category',
    response_description='Jobs',
    status_code=status.HTTP_200_OK,
    response_model=JobsPaginate,
    tags=['jobs'],
)
async def get_all_jobs_for_category(
        category_id: int = Query(default=1, gt=0),
        page: int = Query(default=1, gt=0),
        page_size: int = Query(default=1, gt=0),
        db: AsyncSession = Depends(get_db),
):
    return await views.get_all_jobs_for_category(db=db, page=page, page_size=page_size, category_id=category_id)


@jobs_router.get(
    '/search',
    name='Search jobs',
    description='Search jobs',
    response_description='Jobs',
    status_code=status.HTTP_200_OK,
    response_model=JobsPaginate,
    tags=['jobs'],
)
async def search_jobs(
        search: str,
        page: int = Query(default=1, gt=0),
        page_size: int = Query(default=1, gt=0),
        db: AsyncSession = Depends(get_db),
):
    return await views.search_jobs(db=db, page=page, page_size=page_size, search=search)


@jobs_router.get(
    '/{pk}',
    name='Get job',
    description='Get job',
    response_description='Job',
    status_code=status.HTTP_200_OK,
    response_model=GetJob,
    tags=['jobs'],
)
async def get_job(pk: int, db: AsyncSession = Depends(get_db)):
    return await views.get_job(db, pk)
