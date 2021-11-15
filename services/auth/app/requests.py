import aiohttp
from fastapi import HTTPException

from config import SECRET_QIWI_KEY


async def pay_request(url: str) -> str:
    """
        Pay request
        :param url: URL
        :type url: str
        :return: URL
        :rtype: str
        :raise HTTPException: Bad response
    """

    async with aiohttp.ClientSession() as session:
        response = await session.get(url, allow_redirects=True)

        if not response.ok:
            raise HTTPException(response.status, 'Error')
    return f'{response.url}'


async def check_request(url: str) -> dict:
    """
        Check request
        :param url: URL
        :type url: str
        :return: Data
        :rtype: dict
        :raise HTTPException: Bad response
    """

    async with aiohttp.ClientSession() as session:
        response = await session.get(url, headers={'Authorization': f'Bearer {SECRET_QIWI_KEY}'}, allow_redirects=True)

        json = await response.json()

        if not response.ok:
            raise HTTPException(response.status, json)
    return json
