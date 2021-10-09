import datetime
import os
import typing
from uuid import uuid4

import aiofiles
from fastapi import HTTPException, status, UploadFile, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import VerificationCreate
from app.crud import user_crud, verification_crud
from app.models import User
from app.security import verify_password_hash
from app.send_email import send_register_email
from config import social_auth, SERVER_BACKEND, API
from crud import CRUD


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

        if not await verification_crud.exist(db, user_id=user.id):
            verification = await verification_crud.create(
                db, **VerificationCreate(user_id=user.id, link=str(uuid4())).dict(),
            )
        else:
            verification = await verification_crud.get(db, user_id=user.id)

        send_register_email(user.email, user.username, f'{SERVER_BACKEND}{API}/verify?link={verification.link}')

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


def paginate(crud: CRUD, url: str):
    """
        Paginate
        :param crud: CRUD
        :type crud: CRUD
        :param url: URL
        :type url: str
        :return: Decorator
    """

    def paginate_wrapper(function):
        """
            Decorator
            :param function: Function
            :return: Wrapper
        """

        async def wrapper(*args, **kwargs) -> dict[str, typing.Any]:
            """
                Wrapper
                :param args: args
                :param kwargs: kwargs
                :return: Paginate dict
                :rtype: dict
                :raise HTTPException 400: Results not found
            """

            page: int = kwargs['page']
            page_size: int = kwargs['page_size']
            db: AsyncSession = kwargs['db']
            skip = page_size * (page - 1)
            queryset = await crud.all(db, skip, page_size)

            if not queryset:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Results not found')

            next_page = f'{url}?page={page + 1}&page_size={page_size}' if await crud.exist_page(db, skip + page_size, page_size) else None
            previous_page = None

            if (page - 1) > 0:
                previous_page = f'{url}?page={page - 1}&page_size={page_size}' if await crud.exist_page(db, skip - page_size, page_size) else None

            return {
                'next': next_page,
                'previous': previous_page,
                'page': page,
                'results': await function(*args, queryset=queryset, **kwargs),
            }
        return wrapper
    return paginate_wrapper
