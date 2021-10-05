import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user_crud
from app.models import User
from app.security import verify_password_hash


async def validate_login(db: AsyncSession, username: str, password: str) -> User:
    """
        Validate login data
        :param db: DB
        :type db: AsyncSession
        :param username: Username
        :type username: str
        :param password: Password
        :type password: str
        :return: User
        :rtype: User
        :raise HTTPException 400: Username not found and Password mismatch
        :raise HTTPException 403: You not activated
    """

    if not await user_crud.exist(db, username=username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username not found')

    user = await user_crud.get(db, username=username)

    if not verify_password_hash(password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Password mismatch')

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You not activated')

    await user_crud.update(db, {'id': user.id}, last_login=datetime.datetime.utcnow())

    return user
