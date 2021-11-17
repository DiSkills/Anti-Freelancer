from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import notification_crud
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

    return (
        {
            **notification.__dict__,
            'data': {
                **notification.message.__dict__,
            }
        } for notification in await notification_crud.filter(db, limit=NOTIFICATION_LIMIT, recipient_id=user_id)
    )


async def get_notification(db: AsyncSession, user_id: int, pk: int) -> dict:
    """
        Get notification
        :param db: DB
        :type db: AsyncSession
        :param user_id: User ID
        :type user_id: int
        :param pk: Notification ID
        :type pk: int
        :return: Notification
        :rtype: dict
        :raise HTTPException 400: Notification not found
        :raise HTTPException 400: User not owner this notification
    """

    if not await notification_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Notification not found')
    notification = await notification_crud.get(db, id=pk)

    if notification.recipient_id != user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You not owner this notification')

    return {
        **notification.__dict__,
        'data': {
            **notification.message.__dict__,
        }
    }


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


async def view_notification(db: AsyncSession, user_id: int, pk: int) -> dict[str, str]:
    """
        View notification
        :param db: DB
        :type db: AsyncSession
        :param user_id: User ID
        :type user_id: int
        :param pk: Notification ID
        :type pk: int
        :return: Message
        :rtype: dict
        :raise HTTPException 400: Notification not found
        :raise HTTPException 400: User not owner this notification
    """

    if not await notification_crud.exist(db, id=pk):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Notification not found')
    notification = await notification_crud.get(db, id=pk)

    if notification.recipient_id != user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You not owner this notification')

    await notification_crud.remove(db, id=pk)
    return {'msg': 'Notification has been viewed'}
