import aiohttp
from fastapi import HTTPException

from config import SERVER_AUTH_BACKEND, API


async def get_user_request(user_id: int) -> dict:
    """
        Get user request
        :param user_id: User ID
        :type user_id: int
        :return: User profile
        :rtype: dict
        :raise ValueError: Bad response
    """

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=f'{SERVER_AUTH_BACKEND}{API}/profile/{user_id}')

        json = await response.json()
        if not response.ok:
            raise ValueError(json['detail'])

    return json


async def get_user(user_id: int) -> dict:
    """
        Get user
        :param user_id: User ID
        :type user_id: int
        :return: User profile
        :rtype: dict
    """
    return await get_user_request(user_id)


async def sender_profile_request(token: str) -> dict:
    """
        Sender profile request
        :param token: Token
        :type token: str
        :return: Sender profile
        :rtype: dict
        :raise ValueError: Bad response
    """

    async with aiohttp.ClientSession() as session:
        response = await session.get(
            url=f'{SERVER_AUTH_BACKEND}{API}/profile/current',
            headers={'Authorization': f'Bearer {token}'}
        )

        json = await response.json()
        if not response.ok:
            raise ValueError(json['detail'])

    return json


async def sender_profile(token: str) -> dict:
    """
        Sender profile request
        :param token: Token
        :type token: str
        :return: Sender profile
        :rtype: dict
    """
    return await sender_profile_request(token)


async def get_users_request(ids: list[int]) -> dict:
    """
        Get profiles users request
        :param ids: Users IDs
        :type ids: list
        :return: Profiles
        :rtype: dict
        :raise HTTPException: Bad response
    """

    async with aiohttp.ClientSession() as session:
        response = await session.post(url=f'{SERVER_AUTH_BACKEND}{API}/profile/ids', json=ids)

        json = await response.json()
        if not response.ok:
            raise HTTPException(status_code=response.status, detail=json['detail'])

    return json


async def get_users(ids: list[int]) -> dict:
    """
        Get users profiles
        :param ids: Users IDs
        :type ids: list
        :return: Profiles
        :rtype: dict
    """
    return await get_users_request(ids)
