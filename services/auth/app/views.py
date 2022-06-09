from fastapi import Security, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.crud import user_crud
from app.models import User
from app.tokens import verify_token
from config import SERVER_AUTH_BACKEND, API
from db import async_session

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f'{SERVER_AUTH_BACKEND}{API}/login')


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


async def is_freelancer(user: User = Depends(is_active)) -> User:
    """
        Is freelancer
        :param user: User
        :type user: User
        :return: User
        :rtype: User
        :raise HTTPException 400: User not freelancer
    """

    if not user.freelancer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not freelancer')
    return user


async def is_customer(user: User = Depends(is_active)) -> User:
    """
        Is customer
        :param user: User
        :type user: User
        :return: User
        :rtype: User
        :raise HTTPException 400: User not customer
    """

    if user.freelancer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User not customer')
    return user
