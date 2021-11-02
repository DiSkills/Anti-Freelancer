import aiohttp

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
