from config import PROJECT_NAME
from send_email import send_email


async def send_register_email(user_id: int, recipient: str, username: str, link: str) -> None:
    """
        Send register email
        :param user_id: User ID
        :type user_id: int
        :param recipient: Recipient
        :type recipient: str
        :param username: Username
        :type username: str
        :param link: Link
        :type link: str
        :return: None
    """
    await send_email(
        user_id,
        recipient,
        f'Register email - {PROJECT_NAME}',
        'register.html',
        username=username,
        link=link
    )


async def send_reset_password_email(user_id: int, recipient: str, username: str, link: str) -> None:
    """
        Send reset password email
        :param user_id: User ID
        :type user_id: int
        :param recipient: Recipient
        :type recipient: str
        :param username: Username
        :type username: str
        :param link: Link
        :type link: str
        :return: None
    """
    await send_email(
        user_id,
        recipient,
        f'Reset password email - {PROJECT_NAME}',
        'reset_password.html',
        username=username,
        link=link,
    )


async def send_username_email(user_id: int, recipient: str, username: str) -> None:
    """
        Send username email
        :param user_id: User ID
        :type user_id: int
        :param recipient: Recipient
        :type recipient: str
        :param username: Username
        :type username: str
        :return: None
    """
    await send_email(
        user_id,
        recipient,
        f'Get username email - {PROJECT_NAME}',
        'username.html',
        username=username
    )
