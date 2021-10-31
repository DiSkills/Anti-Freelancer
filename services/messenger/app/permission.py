import aiohttp
from fastapi import Security, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from config import SERVER_AUTH_BACKEND, API, LOGIN_URL

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=LOGIN_URL)


async def permission(url: str, token: str) -> int:
    """
        Permission
        :param url: Url
        :type url: str
        :param token: Token
        :type token: str
        :return: User ID
        :rtype: int
        :raise HTTPException: Bad response
    """

    async with aiohttp.ClientSession() as session:
        response = await session.post(
            url=url, headers={'Authorization': f'Bearer {token}'},
        )

        json = await response.json()
        if not response.ok:
            raise HTTPException(status_code=response.status, detail=json['detail'])

    return json['user_id']


async def is_authenticated(token: str = Security(reusable_oauth2)) -> int:
    """
        Is authenticated
        :param token: Token
        :type token: str
        :return: Response
        :rtype: int
    """
    return await permission(f'{SERVER_AUTH_BACKEND}{API}/is-authenticated', token)


async def is_active(token: str = Security(reusable_oauth2)) -> int:
    """
        Is active
        :param token: Token
        :type token: str
        :return: Response
        :rtype: int
    """
    return await permission(f'{SERVER_AUTH_BACKEND}{API}/is-active', token)


async def is_superuser(token: str = Security(reusable_oauth2)) -> int:
    """
        Is superuser
        :param token: Token
        :type token: str
        :return: Response
        :rtype: int
    """
    return await permission(f'{SERVER_AUTH_BACKEND}{API}/is-superuser', token)


async def is_customer(token: str = Security(reusable_oauth2)) -> int:
    """
        Is customer
        :param token: Token
        :type token: str
        :return: Response
        :rtype: int
    """
    return await permission(f'{SERVER_AUTH_BACKEND}{API}/is-customer', token)


async def is_freelancer(token: str = Security(reusable_oauth2)) -> int:
    """
        Is freelancer
        :param token:Token
        :type token: str
        :return: Response
        :rtype: int
    """
    return await permission(f'{SERVER_AUTH_BACKEND}{API}/is-freelancer', token)
