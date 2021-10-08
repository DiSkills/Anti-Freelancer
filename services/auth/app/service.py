import datetime
import os
import typing

import aiofiles
from fastapi import HTTPException, status, UploadFile, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user_crud
from app.models import User
from app.security import verify_password_hash
from config import social_auth


async def github_data(request: Request) -> dict[str, typing.Any]:
    """
        GitHub request data
        :param request: Request
        :type request: Request
        :return: GitHub data
        :rtype: dict
        :raise HTTPException 400: GitHub error
    """

    try:
        token = await social_auth.github.authorize_access_token(request)
        response = await social_auth.github.get('user', token=token)
    except Exception as _ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='GitHub error')
    github_profile = response.json()
    return github_profile


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


async def write_file(file_name: str, file: UploadFile) -> None:
    """
        Write file
        :param file_name: File name
        :type file_name: str
        :param file: File
        :type file: UploadFile
        :return: None
    """

    async with aiofiles.open(file_name, 'wb') as buffer:
        data = await file.read()
        await buffer.write(data)


def remove_file(file_name: str) -> None:
    """
        Remove file
        :param file_name: File name
        :type file_name: str
        :return: None
    """

    if os.path.exists(file_name):
        os.remove(file_name)
