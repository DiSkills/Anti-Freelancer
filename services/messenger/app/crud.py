import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Message
from app.message.schemas import CreateMessage
from crud import CRUD


class MessageCRUD(CRUD[Message, CreateMessage, CreateMessage]):
    """ Message CRUD """

    @staticmethod
    async def get_all_for_dialog(db: AsyncSession, sender_id: int, recipient_id: int, skip: int = 0, limit: int = 100):
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
    ):
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


message_crud = MessageCRUD(Message)
