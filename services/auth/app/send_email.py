from config import PROJECT_NAME
from send_email import send_email


def send_register_email(recipient, username, link):
    send_email(recipient, f'Register email - {PROJECT_NAME}', 'emails/register.html', username=username, link=link)
