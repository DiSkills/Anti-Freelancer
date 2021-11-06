import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from app.message.schemas import CreateMessage, UpdateMessage
from app.models import Dialogue, Message, Notification
from app.send_email import send_notification_email
from crud import CRUD


class DialogueCRUD(CRUD[Dialogue, Dialogue, Dialogue]):
    """ Dialogue CRUD """

    @staticmethod
    async def get_for_user(db: AsyncSession, user_id: int) -> list[Dialogue]:
        """
            Get dialogues for user
            :param db: DB
            :type db: AsyncSession
            :param user_id: User ID
            :type user_id: int
            :return: Dialogues
            :rtype: list
        """
        query = await db.execute(
            sqlalchemy.select(Dialogue).filter(
                sqlalchemy.or_(
                    sqlalchemy.func.split_part(Dialogue.users_ids, '_', 1) == f'{user_id}',
                    sqlalchemy.func.split_part(Dialogue.users_ids, '_', 2) == f'{user_id}',
                )
            ).order_by(Dialogue.id.desc())
        )
        return query.scalars().all()


class MessageCRUD(CRUD[Message, CreateMessage, UpdateMessage]):
    """ Message CRUD """
    pass


class NotificationCRUD(CRUD[Notification, Notification, Notification]):
    """ Notification CRUD """

    async def create(self, db: AsyncSession, **kwargs) -> Notification:
        """
            Create notification
            :param db: DB
            :type db: AsyncSession
            :param kwargs: kwargs
            :return: New notification
        """
        notification = await super().create(db, **kwargs)
        await send_notification_email(notification)
        return notification

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
