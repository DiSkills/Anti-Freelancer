import aiohttp

from config import SERVER_AUTH_BACKEND, API


async def profile(url: str, headers: dict[str, str] = {}) -> dict:
    """
        Profile
        :param url: URL
        :type url: str
        :param headers: Headers
        :type headers: dict
        :return: User profile
        :rtype: dict
        :raise ValueError: Bad response
    """

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)

        json = await response.json()
        if not response.ok:
            raise ValueError(json['detail'])

    return json


async def get_user(user_id: int) -> dict:
    """
        Get user
        :param user_id: User ID
        :type user_id: int
        :return: User Data (profile)
        :rtype: dict
    """

    return await profile(f'{SERVER_AUTH_BACKEND}{API}/profile/{user_id}')


async def sender_profile(token: str):

    return await profile(f'{SERVER_AUTH_BACKEND}{API}/profile/current', {'Authorization': f'Bearer {token}'})
