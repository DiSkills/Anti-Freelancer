from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user_crud
from app.schemas import Register
from app.service import get_password_hash


async def register(db: AsyncSession, schema: Register):

    if await user_crud.exist(db, username=schema.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username exist')

    if await user_crud.exist(db, email=schema.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email exist')

    del schema.confirm_password
    user = await user_crud.create(db, **{**schema.dict(), 'password': get_password_hash(schema.password)})
    return user
