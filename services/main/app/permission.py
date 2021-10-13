import aiohttp
from fastapi import Security
from fastapi.security import OAuth2PasswordBearer

from config import SERVER_AUTH_BACKEND, API

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f'{SERVER_AUTH_BACKEND}{API}/login')


async def permission(url: str, token: str) -> dict:
    """
        Permission
        :param url: Url
        :type url: str
        :param token: Token
        :type token: str
        :return: Json
        :rtype: dict
    """

    async with aiohttp.ClientSession() as session:
        response = await session.post(
            url=url, headers={'Authorization': f'Bearer {token}'},
        )
    return await response.json()


async def is_authenticated(token: str = Security(reusable_oauth2)) -> dict:
    """
        Is authenticated
        :param token: Token
        :type token: str
        :return: Response
        :rtype: dict
    """
    return await permission(f'{SERVER_AUTH_BACKEND}{API}/is-authenticated', token)


async def is_active(token: str = Security(reusable_oauth2)) -> dict:
    """
        Is active
        :param token: Token
        :type token: str
        :return: Response
        :rtype: dict
    """
    return await permission(f'{SERVER_AUTH_BACKEND}{API}/is-active', token)


async def is_superuser(token: str = Security(reusable_oauth2)) -> dict:
    """
        Is superuser
        :param token: Token
        :type token: str
        :return: Response
        :rtype: dict
    """
    return await permission(f'{SERVER_AUTH_BACKEND}{API}/is-superuser', token)


async def is_customer(token: str = Security(reusable_oauth2)) -> dict:
    """
        Is customer
        :param token: Token
        :type token: str
        :return: Response
        :rtype: dict
    """
    return await permission(f'{SERVER_AUTH_BACKEND}{API}/is-customer', token)


async def is_freelancer(token: str = Security(reusable_oauth2)) -> dict:
    """
        Is freelancer
        :param token:Token
        :type token: str
        :return: Response
        :rtype: dict
    """
    return await permission(f'{SERVER_AUTH_BACKEND}{API}/is-freelancer', token)
