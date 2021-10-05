from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user_crud
from app.security import verify_password_hash


async def validate_login(db: AsyncSession, username: str, password: str):

    if not await user_crud.exist(db, username=username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username not found')

    user = await user_crud.get(db, username=username)

    if not verify_password_hash(password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Password mismatch')

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You not activated')
    return user
