from fastapi import APIRouter, UploadFile, File, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import Message
from app.skills import views
from app.skills.schemas import GetSkill, UpdateSkill, CreateSkill
from app.views import is_superuser
from db import get_db

skills_router = APIRouter()


@skills_router.post(
    '/excel',
    name='Import from excel',
    description='Import from excel',
    response_description='Skills',
    status_code=status.HTTP_201_CREATED,
    response_model=list[GetSkill],
    dependencies=[Depends(is_superuser)],
    tags=['skills'],
)
async def import_from_excel(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    return await views.import_from_excel(db, file)


@skills_router.get(
    '/',
    name='Get all skills',
    description='Get all skills',
    response_description='All skills',
    status_code=status.HTTP_200_OK,
    response_model=list[GetSkill],
    tags=['skills'],
)
async def get_all_skills(db: AsyncSession = Depends(get_db)):
    return await views.get_all_skills(db)


@skills_router.get(
    '/{pk}',
    name='Get skill',
    description='Get skill',
    response_description='Skill',
    status_code=status.HTTP_200_OK,
    response_model=GetSkill,
    tags=['skills'],
)
async def get_skill(pk: int, db: AsyncSession = Depends(get_db)):
    return await views.get_skill(db, pk)


@skills_router.put(
    '/{pk}',
    name='Update skill',
    description='Update skill',
    response_description='Skill',
    status_code=status.HTTP_200_OK,
    response_model=GetSkill,
    dependencies=[Depends(is_superuser)],
    tags=['skills'],
)
async def update_skill(pk: int, schema: UpdateSkill, db: AsyncSession = Depends(get_db)):
    return await views.update_skill(db, schema, pk)


@skills_router.post(
    '/',
    name='Create skill',
    description='Create skill',
    response_description='New skill',
    status_code=status.HTTP_201_CREATED,
    response_model=GetSkill,
    dependencies=[Depends(is_superuser)],
    tags=['skills'],
)
async def create_skill(schema: CreateSkill, db: AsyncSession = Depends(get_db)):
    return await views.create_skill(db, schema)


@skills_router.delete(
    '/{pk}',
    name='Remove skill',
    description='Remove skill',
    response_description='Message',
    status_code=status.HTTP_200_OK,
    response_model=Message,
    dependencies=[Depends(is_superuser)],
    tags=['skills'],
)
async def remove_skill(pk: int, db: AsyncSession = Depends(get_db)):
    return await views.remove_skill(db, pk)
