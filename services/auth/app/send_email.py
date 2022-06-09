from config import PROJECT_NAME
from send_email import send_email


async def send_register_email(recipient: str, username: str, link: str) -> None:
    """
        Send register email
        :param recipient: Recipient
        :type recipient: str
        :param username: Username
        :type username: str
        :param link: Link
        :type link: str
        :return: None
    """
    await send_email(
        recipient,
        f'Register email - {PROJECT_NAME}',
        'register.html',
        username=username,
        link=link
    )


async def send_reset_password_email(recipient: str, username: str, link: str) -> None:
    """
        Send reset password email
        :param recipient: Recipient
        :type recipient: str
        :param username: Username
        :type username: str
        :param link: Link
        :type link: str
        :return: None
    """
    await send_email(
        recipient,
        f'Reset password email - {PROJECT_NAME}',
        'reset_password.html',
        username=username,
        link=link,
    )


async def send_username_email(recipient: str, username: str) -> None:
    """
        Send username email
        :param recipient: Recipient
        :type recipient: str
        :param username: Username
        :type username: str
        :return: None
    """
    await send_email(
        recipient,
        f'Get username email - {PROJECT_NAME}',
        'username.html',
        username=username
    )
