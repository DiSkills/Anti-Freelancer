from config import PROJECT_NAME
from send_email import send_email


def send_register_email(recipient: str, username: str, link: str) -> None:
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
    send_email(recipient, f'Register email - {PROJECT_NAME}', 'emails/register.html', username=username, link=link)


def send_reset_password_email(recipient: str, username: str, link: str) -> None:
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
    send_email(
        recipient, f'Reset password email - {PROJECT_NAME}', 'emails/reset_password.html', username=username, link=link,
    )
