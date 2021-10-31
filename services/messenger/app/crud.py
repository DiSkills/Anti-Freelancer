import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Message
from app.message.schemas import CreateMessage
from crud import CRUD


class MessageCRUD(CRUD[Message, CreateMessage, CreateMessage]):
    """ Message CRUD """

    @staticmethod
    async def get_all_for_dialog(
        db: AsyncSession,
        sender_id: int,
        recipient_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[Message]:
        """
            Get all messages for dialog
            :param db: DB
            :type db: AsyncSession
            :param sender_id: Sender ID
            :type sender_id: int
            :param recipient_id: Recipient ID
            :type recipient_id: int
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :return: Messages
            :rtype: list
        """
        query = await db.execute(
            sqlalchemy.select(Message).filter(
                sqlalchemy.or_(
                    sqlalchemy.and_(
                        Message.sender_id == sender_id,
                        Message.recipient_id == recipient_id,
                    ),
                    sqlalchemy.and_(
                        Message.sender_id == recipient_id,
                        Message.recipient_id == sender_id,
                    )
                )
            ).order_by(Message.id.desc()).offset(skip).limit(limit)
        )
        return query.scalars().all()

    @staticmethod
    async def exist_all_for_dialog(
        db: AsyncSession,
        sender_id: int,
        recipient_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> bool:
        """
            Exist messages for dialog?
            :param db: DB
            :type db: AsyncSession
            :param sender_id: Sender ID
            :type sender_id: int
            :param recipient_id: Recipient ID
            :type recipient_id: int
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :return: Exist messages for dialog?
            :rtype: bool
        """
        query = await db.execute(
            sqlalchemy.exists(
                sqlalchemy.select(Message.id).filter(
                    sqlalchemy.or_(
                        sqlalchemy.and_(
                            Message.sender_id == sender_id,
                            Message.recipient_id == recipient_id,
                        ),
                        sqlalchemy.and_(
                            Message.sender_id == recipient_id,
                            Message.recipient_id == sender_id,
                        )
                    )
                ).order_by(Message.id.desc()).offset(skip).limit(limit)
            ).select()
        )
        return query.scalar()

    @staticmethod
    async def update_viewed(
        db: AsyncSession,
        sender_id: int,
        recipient_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> None:
        """
            Update messages for dialog
            :param db: DB
            :type db: AsyncSession
            :param sender_id: Sender ID
            :type sender_id: int
            :param recipient_id: Recipient ID
            :type recipient_id: int
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :return: None
        """
        query_ids = await db.execute(
            sqlalchemy.select(Message.id).filter(
                sqlalchemy.or_(
                    sqlalchemy.and_(
                        Message.sender_id == sender_id,
                        Message.recipient_id == recipient_id,
                    ),
                    sqlalchemy.and_(
                        Message.sender_id == recipient_id,
                        Message.recipient_id == sender_id,
                    )
                )
            ).order_by(Message.id.desc()).offset(skip).limit(limit)
        )
        ids = query_ids.scalars().all()

        query = sqlalchemy.update(Message).filter(Message.id.in_(ids)).values(viewed=True)
        query.execution_options(synchronize_session="fetch")
        await db.execute(query)
        await db.commit()


message_crud = MessageCRUD(Message)
