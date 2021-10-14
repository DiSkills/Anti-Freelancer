from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.jobs import views
from app.jobs.schemas import CreateJob, GetJob
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
    dependencies=[Depends(is_customer)],
)
async def create_job(schema: CreateJob, db: AsyncSession = Depends(get_db)):
    return await views.create_job(db, schema)
