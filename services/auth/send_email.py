import aiohttp
from fastapi import HTTPException

from app.tokens import create_access_token
from config import TEST, SERVER_EMAIL


async def send_email(user_id: int, recipient: str, subject: str, template: str, **data) -> None:
    """
        Send email
        :param user_id: User ID
        :type user_id: int
        :param recipient: Recipient
        :type recipient: str
        :param subject: Subject
        :type subject: str
        :param template: Template
        :type template: str
        :param data: Jinja data
        :return: None
    """

    if int(TEST):
        return

    async with aiohttp.ClientSession() as session:
        response = await session.post(
            url=f'{SERVER_EMAIL}send', json={
                'recipient': recipient,
                'subject': subject,
                'template': template,
                'data': data,
                'token': create_access_token(user_id)['access_token'],
                'user_id': user_id,
            }
        )

        json = await response.json()
        if not response.ok:
            raise HTTPException(status_code=response.status, detail=json['detail'])

    return json
