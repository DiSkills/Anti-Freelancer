import aiohttp

from app.crud import user_crud
from app.tokens import create_access_token
from config import TEST, SERVER_EMAIL, API, CLIENT_NAME, SERVER_USER_USERNAME
from db import async_session


async def send_email(recipient: str, subject: str, template: str, **data) -> None:
    """
        Send email
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
        async with async_session() as db:
            superuser = await user_crud.get(db, username=SERVER_USER_USERNAME)
            access_token = create_access_token(superuser.id)['access_token']
            response = await session.post(
                url=f'{SERVER_EMAIL}{API}/clients/name?client_name={CLIENT_NAME}',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            json = await response.json()

            if not response.ok:
                raise ValueError(json)

        await session.post(
            url=f'{SERVER_EMAIL}{API}/send', json={
                'recipient': recipient,
                'subject': subject,
                'template': template,
                'data': data,
                'secret': json['secret'],
                'client_name': f'{CLIENT_NAME}',
            }
        )
