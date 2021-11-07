import typing

import aiohttp
from fastapi import HTTPException

from config import SERVER_AUTH_BACKEND, API, SERVER_USER_USERNAME, SERVER_USER_PASSWORD, TEST


async def get_user(user_id: int) -> dict:
    """
        Get user
        :param user_id: User ID
        :type user_id: int
        :return: User Data (profile)
        :rtype: dict
        :raise HTTPException status: Bad response
    """

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=f'{SERVER_AUTH_BACKEND}{API}/profile/{user_id}')

        json = await response.json()
        if not response.ok:
            raise HTTPException(status_code=response.status, detail=json['detail'])

    return json


async def get_server_token(session: aiohttp.ClientSession):
    response = await session.post(
        url=f'{SERVER_AUTH_BACKEND}{API}/login',
        data={'username': SERVER_USER_USERNAME, 'password': SERVER_USER_PASSWORD}
    )
    response.raise_for_status()
    json = await response.json()

    return json['access_token']


async def get_user_data_and_server_token(user_id: int) -> typing.Optional[tuple[str, dict]]:
    """
        Get user data and server token
        :param user_id: User ID
        :type user_id: int
        :return: Server token and user data
        :rtype: tuple
    """
    if int(TEST):
        return

    async with aiohttp.ClientSession() as session:
        access_token = await get_server_token(session)
        headers = {'Authorization': f'Bearer {access_token}'}

        response = await session.get(url=f'{SERVER_AUTH_BACKEND}{API}/admin/user/{user_id}', headers=headers)
        response.raise_for_status()
        json = await response.json()
    return access_token, json


async def update_level(user_id: int, level: int) -> None:
    """
        Update level
        :param user_id: User ID
        :type user_id: int
        :param level: Level
        :type level: int
        :return: None
    """

    if int(TEST):
        return

    async with aiohttp.ClientSession() as session:
        access_token = await get_server_token(session)
        headers = {'Authorization': f'Bearer {access_token}'}

        response = await session.put(
            url=f'{SERVER_AUTH_BACKEND}{API}/admin/user/level/{user_id}?level={level}',
            headers=headers
        )
        response.raise_for_status()
