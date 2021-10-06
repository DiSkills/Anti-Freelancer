import os
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status, Security, Depends, UploadFile
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user_crud, verification_crud
from app.models import User
from app.schemas import Register, VerificationCreate, UserChangeData
from app.security import get_password_hash
from app.send_email import send_register_email
from app.service import validate_login, remove_file, write_file
from app.tokens import create_login_tokens, verify_token, create_access_token
from config import SERVER_BACKEND, API, MEDIA_ROOT
from db import async_session

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl='/api/v1/login')


async def register(db: AsyncSession, schema: Register) -> dict[str, str]:
    """
        Register
        :param db: DB
        :type db: AsyncSession
        :param schema: Register data
        :type schema: Register
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Username or email exist
    """

    if await user_crud.exist(db, username=schema.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username exist')

    if await user_crud.exist(db, email=schema.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email exist')

    del schema.confirm_password
    user = await user_crud.create(db, **{**schema.dict(), 'password': get_password_hash(schema.password)})

    verification = await verification_crud.create(db, **VerificationCreate(user_id=user.id, link=str(uuid4())).dict())

    send_register_email(user.email, user.username, f'{SERVER_BACKEND}{API}/verify?link={verification.link}')

    return {'msg': 'Send email for activate your account'}


async def verify(db: AsyncSession, link: str) -> dict[str, str]:
    """
        Verification account
        :param db: DB
        :type db: AsyncSession
        :param link: Link
        :type link: str
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Verification not found
    """

    if not await verification_crud.exist(db, link=link):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification not exist')

    verification = await verification_crud.get(db, link=link)
    await user_crud.update(db, {'id': verification.user_id}, is_active=True)
    await verification_crud.remove(db, id=verification.id)
    return {'msg': 'Your account has been activated'}


async def login(db: AsyncSession, username: str, password: str) -> dict[str, str]:
    """
        Login user
        :param db: DB
        :type db: AsyncSession
        :param username: Username
        :type username: str
        :param password: Password
        :type password: str
        :return: Tokens
        :rtype: dict
    """
    user = await validate_login(db, username, password)
    return create_login_tokens(user.id)


async def refresh(db: AsyncSession, token: str) -> dict[str, str]:
    """
        Refresh
        :param db: DB
        :type db: AsyncSession
        :param token: Refresh token
        :type token: str
        :return: Access token and token type
        :rtype: dict
    """

    user_id = await verify_token(db, token, 'refresh', 'Refresh token not found')

    return create_access_token(user_id)


async def is_authenticated(token: str = Security(reusable_oauth2)) -> int:
    """
        Is authenticated
        :param token: Access token
        :type token: str
        :return: User ID
        :rtype: int
    """
    async with async_session() as db:
        return await verify_token(db, token, 'access', 'Access token not found')


async def is_active(user_id: int = Depends(is_authenticated)) -> User:
    """
        Is active
        :param user_id: User ID
        :type user_id: int
        :return: User ID
        :rtype: User
        :raise HTTPException 403: User not activated
    """

    async with async_session() as db:
        user = await user_crud.get(db, id=user_id)

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not activated')
    return user


async def is_superuser(user: User = Depends(is_active)) -> User:
    """
        Is superuser
        :param user: User
        :type user: User
        :return: User ID
        :rtype: User
        :raise HTTPException 403: User not superuser
    """

    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not superuser')
    return user


async def avatar(db: AsyncSession, user: User, file: UploadFile) -> dict[str, str]:
    """
        Avatar
        :param db: DB
        :type db: AsyncSession
        :param user: User
        :type user: User
        :param file: File
        :type file: UploadFile
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Avatar only in png format
    """

    if file.content_type != 'image/png':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Avatar only in png format')

    if (user.avatar is not None) and (MEDIA_ROOT in user.avatar):
        remove_file(user.avatar)

    if not os.path.exists(MEDIA_ROOT + user.username):
        os.mkdir(MEDIA_ROOT + user.username)

    avatar_name = f'{MEDIA_ROOT}{user.username}/{datetime.utcnow().timestamp()}.png'

    await write_file(avatar_name, file)
    await user_crud.update(db, {'id': user.id}, avatar=avatar_name)
    return {'msg': 'Avatar has been saved'}


async def change_data(db: AsyncSession, schema: UserChangeData, user: User) -> dict:
    """
        Change data
        :param db: DB
        :type db: AsyncSession
        :param schema: Changed data
        :type schema: UserChangeData
        :param user: User
        :type user: User
        :return: User data
        :rtype: dict
    """

    if user.username != schema.username:
        if await user_crud.exist(db, username=schema.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username exist')
    else:
        del schema.username

    if user.email != schema.email:
        if await user_crud.exist(db, email=schema.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email exist')
    else:
        del schema.email

    user = await user_crud.update(db, {'id': user.id}, **schema.dict())
    return user.__dict__
