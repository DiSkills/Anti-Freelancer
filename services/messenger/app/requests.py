import aiohttp

from config import SERVER_AUTH_BACKEND, API


async def sender_profile_request(token: str) -> dict:

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
    return await sender_profile_request(token)
