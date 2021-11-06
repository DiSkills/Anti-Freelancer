from app.models import Notification
from app.requests import get_user_data_and_server_token
from config import TEST, PROJECT_NAME, SERVER_MESSENGER_BACKEND, API
from send_email import send_email


async def send_notification_email(notification: Notification) -> None:
    """
        Send notification email
        :param notification: Notification
        :type notification: Notification
        :return: None
    """

    if int(TEST):
        return

    server_token, user_data = await get_user_data_and_server_token(notification.recipient_id)
    await send_email(
        server_token,
        user_data['email'],
        f'{notification.type.lower().title()} message email - {PROJECT_NAME}',
        'notification.html',
        username=user_data['username'],
        link=f'{SERVER_MESSENGER_BACKEND}{API}/notifications/{notification.id}',
    )
