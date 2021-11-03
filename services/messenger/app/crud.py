import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from app.message.schemas import CreateMessage
from app.models import Dialogue, Message, Notification
from crud import CRUD


class DialogueCRUD(CRUD[Dialogue, Dialogue, Dialogue]):
    """ Dialogue CRUD """
    pass


class MessageCRUD(CRUD[Message, CreateMessage, CreateMessage]):
    """ Message CRUD """
    pass


class NotificationCRUD(CRUD[Notification, Notification, Notification]):
    """ Notification CRUD """

    @staticmethod
    async def filter_ids(db: AsyncSession, skip: int = 0, limit: int = 100, **kwargs) -> list[Notification]:
        """
            Get notifications ids
            :param db: DB
            :type db: AsyncSession
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :param kwargs: Filter params
            :return: Notifications
            :rtype: list
        """
        query = await db.execute(
            sqlalchemy.select(Notification.sender_id).filter_by(
                **kwargs
            ).order_by(Notification.id.desc()).offset(skip).limit(limit)
        )
        return query.scalars().all()

    @staticmethod
    async def view(db: AsyncSession, skip: int = 0, limit: int = 100, **kwargs) -> None:
        """
            View notifications
            :param db: DB
            :type db: AsyncSession
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :param kwargs: Filter params
            :return: None
        """

        query = await db.execute(
            sqlalchemy.select(Notification.id).filter_by(
                **kwargs
            ).order_by(Notification.id.desc()).offset(skip).limit(limit)
        )
        query = query.scalars().all()

        await db.execute(
            sqlalchemy.delete(Notification).filter_by(
                **kwargs
            ).filter(
                Notification.id.in_(query)
            )
        )
        await db.commit()


dialogue_crud = DialogueCRUD(Dialogue)
message_crud = MessageCRUD(Message)
notification_crud = NotificationCRUD(Notification)
