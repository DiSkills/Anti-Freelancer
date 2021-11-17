import typing

import aiohttp

from config import SERVER_AUTH_BACKEND, API, SERVER_USER_PASSWORD, SERVER_USER_USERNAME, TEST


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


async def get_sender_data_request(user_id: int) -> dict:
    """
        Get sender data request
        :param user_id: User ID
        :type user_id: int
        :return: Sender profile
        :rtype: dict
        :raise ValueError: Bad response
    """

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=f'{SERVER_AUTH_BACKEND}{API}/profile/{user_id}')

        json = await response.json()
        if not response.ok:
            raise ValueError(json['detail'])

    return json


async def get_sender_data(user_id: int) -> dict:
    """
        Sender profile
        :param user_id: User ID
        :type user_id: int
        :return: Sender profile
        :rtype: dict
    """
    return await get_sender_data_request(user_id)


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
        response = await session.post(
            url=f'{SERVER_AUTH_BACKEND}{API}/login',
            data={'username': SERVER_USER_USERNAME, 'password': SERVER_USER_PASSWORD}
        )
        response.raise_for_status()
        json = await response.json()

        access_token = json['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}

        response = await session.get(url=f'{SERVER_AUTH_BACKEND}{API}/admin/user/{user_id}', headers=headers)
        response.raise_for_status()
        json = await response.json()
    return access_token, json
