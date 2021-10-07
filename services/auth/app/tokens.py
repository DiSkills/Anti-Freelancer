import datetime
from functools import wraps

import jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user_crud
from config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, RESET_TOKEN_EXPIRE_MINUTES

ALGORITHM = 'HS256'


def create_jwt_token(data: dict, subject: str, expires_delta: datetime.timedelta = None) -> str:
    """
        Create token
        :param data: Data
        :type data: dict
        :param subject: Subject
        :type subject: str
        :param expires_delta: Expires
        :type expires_delta: timedelta
        :return: Token
        :rtype: str
    """
    encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    encode.update({'exp': expire, 'sub': subject})
    encoded_jwt = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(user_id: int) -> dict[str, str]:
    """
        Create access token
        :param user_id: User ID
        :type user_id: int
        :return: Access token and token type
        :rtype: dict
    """

    expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        'access_token': create_jwt_token({'user_id': user_id}, 'access', expires),
        'type': 'bearer',
    }


def create_refresh_token(user_id: int) -> dict[str, str]:
    """
        Create refresh token
        :param user_id: User ID
        :type user_id: int
        :return: Refresh token and token type
        :rtype: dict
    """

    expires = datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    return {
        'refresh_token': create_jwt_token({'user_id': user_id}, 'refresh', expires),
        'type': 'bearer',
    }


def create_reset_password_token(user_id: int) -> str:

    expires = datetime.timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    return create_jwt_token({'user_id': user_id}, 'reset', expires)


def create_login_tokens(user_id: int) -> dict[str, str]:
    """
        Create login tokens
        :param user_id: User ID
        :type user_id: int
        :return: Tokens and tokens type
        :rtype: dict
    """
    return {**create_access_token(user_id), **create_refresh_token(user_id)}


async def verify_token(db: AsyncSession, token: str, sub: str, error_message: str) -> int:
    """
        Verify token
        :param db: DB
        :type db: AsyncSession
        :param token: Token
        :type token: str
        :param sub: Subject
        :type sub: str
        :param error_message: Error message
        :type error_message: str
        :return: User ID
        :rtype: int
        :raise HTTPException 400: Error message or User not found
        :raise HTTPException 401: Token lifetime ended
        :raise HTTPException 403: Could not validate credentials
    """

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded['sub'] != sub:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

        if not await user_crud.exist(db, id=decoded['user_id']):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User not found')

        await user_crud.update(db, {'id': decoded['user_id']}, last_login=datetime.datetime.utcnow())

        return decoded['user_id']
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token lifetime ended')
    except jwt.exceptions.PyJWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Could not validate credentials')
