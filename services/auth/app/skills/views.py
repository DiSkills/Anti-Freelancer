import io
import typing

from fastapi import UploadFile, HTTPException, status
from pandas import DataFrame, read_excel
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import skill_crud
from app.skills.schemas import UpdateSkill, CreateSkill


async def import_from_excel(db: AsyncSession, file: UploadFile) -> list[dict[str, typing.Union[int, str]]]:

    if file.content_type != 'application/vnd.ms-excel':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File only format xls (excel)')

    data: DataFrame = read_excel(io.BytesIO(await file.read()))
    return await skill_crud.create_from_file(db, data.values)


async def get_all_skills(db: AsyncSession):
    return (skill.__dict__ for skill in await skill_crud.all(db, limit=1000))


async def get_skill(db: AsyncSession, pk: int) -> dict[str, typing.Union[int, str]]:

    if not await skill_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Skill not found')

    skill = await skill_crud.get(db, id=pk)
    return skill.__dict__


async def update_skill(db: AsyncSession, schema: UpdateSkill, pk: int) -> dict[str, typing.Union[int, str]]:

    if not await skill_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Skill not found')

    if await skill_crud.exist(db, name=schema.name):
        skill = await skill_crud.get(db, name=schema.name)
        if skill.id != pk:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Skill name exist')

    if await skill_crud.exist(db, image=schema.image):
        skill = await skill_crud.get(db, image=schema.image)
        if skill.id != pk:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Skill image exist')

    skill = await skill_crud.update(db, {'id': pk}, **schema.dict())
    return skill.__dict__


async def create_skill(db: AsyncSession, schema: CreateSkill) -> dict[str, typing.Union[int, str]]:

    if await skill_crud.exist(db, name=schema.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Skill name exist')
    if await skill_crud.exist(db, image=schema.image):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Skill image exist')
    skill = await skill_crud.create(db, **schema.dict())
    return skill.__dict__


async def remove_skill(db: AsyncSession, pk: int) -> dict[str, str]:

    if not await skill_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Skill not found')
    await skill_crud.remove(db, id=pk)
    return {'msg': 'Skill has been deleted'}
