import aiohttp

from config import TEST, SERVER_EMAIL, API, CLIENT_NAME


async def send_email(server_token: str, recipient: str, subject: str, template: str, **data) -> None:
    """
        Send email
        :param server_token: Server token
        :type server_token: str
        :param recipient: Recipient
        :type recipient: str
        :param subject: Subject
        :type subject: str
        :param template: Template
        :type template: str
        :param data: data
        :return: None
    """
    if int(TEST):
        return

    async with aiohttp.ClientSession() as session:
        response = await session.post(
            url=f'{SERVER_EMAIL}{API}/clients/name?client_name={CLIENT_NAME}',
            headers={'Authorization': f'Bearer {server_token}'}
        )
        response.raise_for_status()
        json = await response.json()

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
