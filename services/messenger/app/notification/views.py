from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import notification_crud
from app.requests import get_users
from config import NOTIFICATION_LIMIT


async def get_notifications(db: AsyncSession, user_id: int):
    """
        Get notifications
        :param db: DB
        :type db: AsyncSession
        :param user_id: User ID
        :type user_id: int
        :return: Notifications for user
    """

    ids = await notification_crud.filter_ids(db, limit=NOTIFICATION_LIMIT, recipient_id=user_id)

    users = await get_users(ids)

    return (
        {
            **notification.__dict__,
            'data': {
                **notification.message.__dict__,
                'sender': users[f'{notification.sender_id}'],
            }
        } for notification in await notification_crud.filter(db, limit=NOTIFICATION_LIMIT, recipient_id=user_id)
    )


async def view_notifications(db: AsyncSession, user_id: int) -> dict[str, str]:
    """
        View notifications
        :param db: DB
        :type db: AsyncSession
        :param user_id: User ID
        :type user_id: int
        :return: Message
        :rtype: dict
    """

    await notification_crud.view(db, limit=NOTIFICATION_LIMIT, recipient_id=user_id)

    if await notification_crud.exist(db, recipient_id=user_id):
        return {'msg': 'Notifications has been viewed. You have more notifications'}
    return {'msg': 'Notifications has been viewed. You don\'t have more notifications'}
